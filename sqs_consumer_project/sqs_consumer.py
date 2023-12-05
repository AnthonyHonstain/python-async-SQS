import asyncio

import botocore.exceptions
from aiobotocore.session import get_session
import sys

from sqs_consumer_project.async_worker import do_work


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
            print(f'Pulling messages off the queue - {consumer_name}')
            try:
                response = await client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=2,
                )

                if 'Messages' in response:
                    for msg in response['Messages']:
                        message_body = msg['Body']

                        await do_work(consumer_name)
                        # print(f'{id} Started')
                        # await asyncio.sleep(5)
                        # print(f'{id} Complete')

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
