import asyncio
import logging

from models import SearchOutcome
from models import SearchResult
from providers.stackoverflow import search_stackoverflow
from providers.wikipedia import search_wikipedia
from providers.github import search_github

logger = logging.getLogger(__name__)

DICT_OF_SOURCES =  {
    "Wikipedia": search_wikipedia,
    "GitHub": search_github,
    "Stack Overflow": search_stackoverflow
    }

async def search_all(query: str) -> SearchOutcome:
    new_list = []
    down_sources = []

    search_all_providers = await asyncio.gather(*(provider_func(query) for provider_func in DICT_OF_SOURCES.values()), return_exceptions=True)
    for source, one_provider in zip(DICT_OF_SOURCES, search_all_providers):
        if isinstance(one_provider, Exception):
            logger.error("Provider %s failed: %r", source, one_provider)
            down_sources.append(source)
        else:
            new_list.extend(one_provider)
    return SearchOutcome(results=new_list, failed_sources=down_sources, total_sources=len(DICT_OF_SOURCES))

async def search_all_sequential(query: str) -> list[SearchResult]: # Only for benchmark; lists providers manually and does not follow DICT_OF_SOURCES
    providers_results = []
    providers_results.extend(await search_wikipedia(query))
    providers_results.extend(await search_github(query))
    providers_results.extend(await search_stackoverflow(query))
    return providers_results





async def main() -> None:
    result= await search_all("python")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())