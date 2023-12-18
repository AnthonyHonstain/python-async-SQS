import httpx
from pydantic import ValidationError

from sqs_consumer_project.models.Message import MessageModel
from sqs_consumer_project.models.record_user_response import RecordUserResponse


async def do_work(worker_id: int, message: MessageModel) -> MessageModel:
    print(f"worker_id:{worker_id} Started on name:{message.name} age:{message.age}")

    # This is used for testing this worker under unusual delays.
    # await asyncio.sleep(5)

    message.age += 1
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8080/record_user", json=message.model_dump_json())
        response.raise_for_status()

        try:
            record_user_response = RecordUserResponse(**response.json())
        except ValidationError as e:
            print(f"worker_id:{worker_id} {e.errors()}")
            raise e

        print(f"worker_id:{worker_id} response user_id:{record_user_response.user_id}")

    print(f"worker_id:{worker_id} Complete on name:{message.name} age:{message.age}")
    return message
