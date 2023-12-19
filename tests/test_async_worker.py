import pytest
import respx
from httpx import Response, HTTPStatusError
from pydantic import ValidationError

from sqs_consumer_project.async_worker import do_work
from sqs_consumer_project.models.example_sqs_message import ExampleSQSMessageModel


@pytest.mark.asyncio
@respx.mock
async def test_do_work__successful_post():
    url = "http://localhost:8080/record_user"  # Adjust this to the actual URL
    expected_content = b'"{\\"name\\":\\"Test Name\\",\\"age\\":21}"'

    post_route = respx.post(url).mock(return_value=Response(200, json={"user_id": "123"}))

    worker_id = 1
    test_message = ExampleSQSMessageModel(name="Test Name", age=20)

    result = await do_work(worker_id, test_message)

    assert result.age == 21
    assert result.name == "Test Name"

    assert post_route.called
    assert post_route.call_count == 1
    assert post_route.calls.last.request.content == expected_content


@pytest.mark.asyncio
@respx.mock
async def test_do_work__failed_post():
    url = "http://localhost:8080/record_user"  # Adjust this to the actual URL
    respx.post(url).mock(return_value=Response(500, json={"user_id": "123"}))

    worker_id = 1
    test_message = ExampleSQSMessageModel(name="Test Name", age=20)

    with pytest.raises(HTTPStatusError):
        await do_work(worker_id, test_message)


@pytest.mark.asyncio
@respx.mock
async def test_do_work__expected_post_result():
    url = "http://localhost:8080/record_user"  # Adjust this to the actual URL
    respx.post(url).mock(return_value=Response(200, json={"UNKNOWN": "123"}))

    worker_id = 1
    test_message = ExampleSQSMessageModel(name="Test Name", age=20)

    with pytest.raises(ValidationError):
        await do_work(worker_id, test_message)
