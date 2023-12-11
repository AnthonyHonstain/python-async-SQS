import asyncio
import json

import botocore.exceptions
import pydantic
from aiobotocore.session import get_session
import sys

from sqs_consumer_project.async_worker import do_work
from sqs_consumer_project.models.Message import MessageModel


async def consume_message(queue_name: str, consumer_name: int, shutdown_signal: asyncio.Event):
    async with get_session().create_client(
            'sqs',
            region_name='us-east-1',
            endpoint_url='http://localhost:4566',
            aws_access_key_id='test',
            aws_secret_access_key='test'
    ) as client:
        try:
            response = await client.get_queue_url(QueueName=queue_name)
        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                print(f"Queue {queue_name} does not exist")
                sys.exit(1)
            else:
                raise

        queue_url = response['QueueUrl']

        while not shutdown_signal.is_set():
            print(f'consumer_name:{consumer_name} Pulling messages off the queue')
            try:
                response = await client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=2,
                )

                if 'Messages' in response:
                    for msg in response['Messages']:
                        message_id = msg['MessageId']
                        message_body = msg['Body']
                        print(f'consumer_name:{consumer_name} Starting MessageId:{message_id}')
                        try:
                            message_dict = json.loads(message_body)
                            message_data = MessageModel.model_validate(message_dict)
                            print(message_data)
                        except pydantic.ValidationError as e:
                            print(f'Invalid message format: {e}')

                        await do_work(consumer_name)

                        # Need to remove msg from queue or else it'll reappear, you could see this by
                        # checking ApproximateNumberOfMessages and ApproximateNumberOfMessagesNotVisible
                        # in the queue.
                        await client.delete_message(
                            QueueUrl=queue_url,
                            ReceiptHandle=msg['ReceiptHandle'],
                        )
                else:
                    print('No messages in queue')
            except asyncio.CancelledError:
                print('Cancel Error')
                break
            # except KeyboardInterrupt:
            #     break

        print('Finished')


async def main():
    queue_name = 'my-queue2'
    consumer_count = 1
    shutdown_signal = asyncio.Event()
    consumers = [consume_message(queue_name, consumer_name, shutdown_signal) for consumer_name in range(consumer_count)]
    await asyncio.gather(*consumers)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Script interrupted by user")
