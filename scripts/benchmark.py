import asyncio

from typing import Any
from collections.abc import Callable, Awaitableп
from time import perf_counter
from search_service import search_all, search_all_sequential


async def measure_time(search_func: Callable[[str], Awaitable[Any]], query: str) -> float:
    start = perf_counter()
    await search_func(query)
    end = perf_counter()
    return end - start


async def main() -> None:
    time_results_gather = []
    time_results_sequential = []
    for _ in range(5):
         time_results_gather.append(await measure_time(search_all, "python"))

    for _ in range(5):
        time_results_sequential.append(await measure_time(search_all_sequential, "python"))


    print(time_results_gather)
    print(time_results_sequential)



if __name__ == '__main__':
    asyncio.run(main())