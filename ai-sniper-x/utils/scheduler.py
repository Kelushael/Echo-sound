import asyncio
from typing import Callable


async def periodic(delay: float, func: Callable, *args, **kwargs):
    while True:
        await func(*args, **kwargs)
        await asyncio.sleep(delay)
