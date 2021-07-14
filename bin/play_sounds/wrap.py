from asyncio import Task, create_task
from functools import partial, wraps
from typing import Any, Awaitable, Callable

from anyio.to_thread import run_sync


async def to_thread(func: Callable, *args, **kwargs) -> Any:
    """Asynchronus partial function"""
    new_func = partial(func, *args, **kwargs)
    return await run_sync(new_func)


async def to_thread_task(func: Callable, *args, **kwargs) -> Task:
    """Assign task to thread"""
    coro = to_thread(func, *args, **kwargs)
    return create_task(coro)


async def finalize_task(task: Task) -> Any:
    """Wait for task or cancel if not cancelled"""
    try:
        return await task

    finally:
        if not task.cancelled():
            task.cancel()


CoroutineResult = Awaitable[Any]
CoroutineFunction = Callable[..., CoroutineResult]
CoroutineMethod = Callable[..., CoroutineResult]


def func_as_method_coro(func: Callable) -> CoroutineMethod:
    """Wrapper function to func"""

    @wraps(func)
    async def method(*args, **kwargs) -> Any:
        return await to_thread(func, *args, **kwargs)

    return method


def coro_as_method_coro(coro: CoroutineFunction) -> CoroutineMethod:
    """Wrapper function to coro"""

    @wraps(coro)
    async def method(*args, **kwargs) -> Any:
        return await coro(*args, **kwargs)

    return method
