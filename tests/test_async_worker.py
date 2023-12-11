import pytest

from sqs_consumer_project.async_worker import do_work
from sqs_consumer_project.models.Message import MessageModel


@pytest.mark.asyncio
async def test_do_work():
    worker_id = 1
    test_message = MessageModel(name="Test Name", age=20)

    result = await do_work(worker_id, test_message)

    assert result.age == 21
    assert result.name == "Test Name"
