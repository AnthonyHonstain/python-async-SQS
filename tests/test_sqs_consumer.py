import pytest
import asyncio
from aiobotocore.session import get_session

from sqs_consumer_project.sqs_consumer import consume_message

QUEUE_NAME = "test-my-queue2"


# TODO - wasn't able to figure out how to inject this, I experimented some with pytest_asyncio
#  (reference https://stackoverflow.com/a/73019163) but wasn't able to get this working.
# @pytest.fixture(scope="session")
# async def sqs_client():
#     async with get_session().create_client(
#             'sqs',
#             region_name='us-east-1',
#             endpoint_url='http://localhost:4566',
#             aws_access_key_id='test',
#             aws_secret_access_key='test'
#     ) as client:
#         yield client


@pytest.mark.asyncio
async def test_sqs_consumer():
    shutdown_signal = asyncio.Event()

    async with get_session().create_client(
        "sqs",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    ) as sqs_client:
        # Create the queue
        response = await sqs_client.create_queue(QueueName=QUEUE_NAME)

        queue_url = response["QueueUrl"]

        response = await sqs_client.list_queues()

        print("Queue URLs:")
        for queue_name in response.get("QueueUrls", []):
            print(f" {queue_name}")

        # Send a message
        test_message = '{"name": "Anthony", "age":2, "unknown":"unknown-fields"}'
        await sqs_client.send_message(QueueUrl=QUEUE_NAME, MessageBody=test_message)

        # Wait a bit to ensure the message is processed
        await asyncio.sleep(0.25)  # Adjust the sleep time as needed

        # Start the consumer in a background task
        consumer_task = asyncio.create_task(consume_message(QUEUE_NAME, 666, shutdown_signal))

        # Wait a bit to ensure the message is processed
        await asyncio.sleep(0.25)  # Adjust the sleep time as needed

        # TODO - the system doesn't do anything and hence we don't have anything
        #  to test here, but this is where we would verify the consumer did something

        # Signal the consumer to shut down
        shutdown_signal.set()

        # Wait for the consumer to finish
        await consumer_task
