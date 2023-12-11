from sqs_consumer_project.models.Message import MessageModel


async def do_work(worker_id: int, message: MessageModel) -> MessageModel:
    print(f"{worker_id} Started on name:{message.name} age:{message.age}")
    # await asyncio.sleep(5)
    message.age += 1

    print(f"{worker_id} Complete on name:{message.name} age:{message.age}")
    return message
