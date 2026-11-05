import asyncio
import search_service

from time import perf_counter
from models import SearchResult



counters = {
    "Wikipedia":      {"current": 0, "max": 0},
    "GitHub":         {"current": 0, "max": 0},
    "Stack Overflow": {"current": 0, "max": 0},
}
def make_fake_provider(name: str):
    async def fake_provider(query: str) -> list[SearchResult]:
        counters[name]["current"] += 1
        if counters[name]["current"] > counters[name]["max"]:
            counters[name]["max"] = counters[name]["current"]
        try:
            await asyncio.sleep(0.3)
        finally:
            counters[name]["current"] -= 1
        return []
    return fake_provider

fake_sources = {}
for name in search_service.DICT_OF_SOURCES:
    fake_sources[name] = make_fake_provider(name)

async def main() -> None:
    search_service.DICT_OF_SOURCES = fake_sources
    start = perf_counter()
    results = await asyncio.gather(*(search_service.search_all("test") for _ in range(100)))
    end = perf_counter() - start
    print(f"Time: {end:.2f} s")
    print(counters)
    print("Failed:", sum(1 for r in results if r.failed_sources))

if __name__ == "__main__":
    asyncio.run(main())