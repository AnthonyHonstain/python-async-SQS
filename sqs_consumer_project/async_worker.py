import httpx
from httpx import HTTPError
from pydantic import ValidationError

from sqs_consumer_project.models.example_sqs_message import ExampleSQSMessageModel
from sqs_consumer_project.models.record_user_response import RecordUserResponse


async def do_work(worker_id: int, message: ExampleSQSMessageModel) -> bool:
    print(f"worker_id:{worker_id} Started on name:{message.name} age:{message.age}")

    # This is used for testing this worker under unusual delays.
    # await asyncio.sleep(5)

    message.age += 1  # Not a higher purpose here, just mutating the data to simulate "work"

    async with httpx.AsyncClient() as client:
        json_body = message.model_dump_json()

        try:
            response = await client.post("http://localhost:8080/record_user", json=json_body)
            response.raise_for_status()
        except HTTPError as exc:
            print(f"worker_id:{worker_id} Failed with HTTP error {exc}")
            return False

        try:
            record_user_response = RecordUserResponse(**response.json())
            print(f"worker_id:{worker_id} response user_id:{record_user_response.user_id}")
        except ValidationError as e:
            print(f"worker_id:{worker_id} Failed to deserialize response {e}")
            return False

    print(f"worker_id:{worker_id} Complete on name:{message.name} age:{message.age}")
    return True
