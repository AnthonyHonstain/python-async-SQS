import asyncio


async def do_work(worker_id: int):
    print(f'{worker_id} Started')
    await asyncio.sleep(5)
    print(f'{worker_id} Complete')

