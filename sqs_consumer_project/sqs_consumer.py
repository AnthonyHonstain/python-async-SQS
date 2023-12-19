import asyncio
import json
import sys

import botocore.exceptions
import pydantic
from aiobotocore.session import get_session

from sqs_consumer_project.async_worker import do_work
from sqs_consumer_project.models.example_sqs_message import ExampleSQSMessageModel


async def consume_messages(queue_name: str, consumer_name: int, shutdown_signal: asyncio.Event):
    async with get_session().create_client(
        "sqs",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    ) as client:
        try:
            get_url_response = await client.get_queue_url(QueueName=queue_name)
        except botocore.exceptions.ClientError as err:
            if err.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                print(f"Queue {queue_name} does not exist")
                sys.exit(1)
            else:
                raise

        queue_url = get_url_response["QueueUrl"]

        while not shutdown_signal.is_set():
            print(f"consumer_name:{consumer_name} Pulling messages off the queue")
            try:
                receive_message_response = await client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=2,
                )

                if "Messages" in receive_message_response:
                    for msg in receive_message_response["Messages"]:
                        message_id = msg["MessageId"]
                        message_body = msg["Body"]
                        successfully_processed = await message_processor(consumer_name, message_id, message_body)

                        if successfully_processed:
                            # Need to remove msg from queue or else it'll reappear, you could see this by
                            # checking ApproximateNumberOfMessages and ApproximateNumberOfMessagesNotVisible
                            # in the queue.
                            await client.delete_message(
                                QueueUrl=queue_url,
                                ReceiptHandle=msg["ReceiptHandle"],
                            )
                        else:
                            print(f"consumer_name:{consumer_name} Failed to process message")
                else:
                    print(f"consumer_name:{consumer_name} No messages in queue")
            except asyncio.CancelledError:
                print(f"consumer_name:{consumer_name} Cancel Error")
                break
            # except KeyboardInterrupt:
            #     break

        print("Finished")


async def message_processor(consumer_name: int, message_id: str, message_body: str) -> bool:
    print(f"consumer_name:{consumer_name} Starting MessageId:{message_id}")
    try:
        message_dict = json.loads(message_body)
        message = ExampleSQSMessageModel.model_validate(message_dict)
        print(f"consumer_name:{consumer_name} pydantic model: {message}")
    except pydantic.ValidationError as e:
        print(f"consumer_name:{consumer_name} Invalid message format: {e}")
        return False

    await do_work(consumer_name, message)
    return True


async def main():
    queue_name = "my-queue2"
    consumer_count = 2
    shutdown_signal = asyncio.Event()
    consumers = [
        consume_messages(queue_name, consumer_name, shutdown_signal) for consumer_name in range(consumer_count)
    ]
    await asyncio.gather(*consumers)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Script interrupted by user")
