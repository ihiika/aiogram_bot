import asyncio
import logging

from models import SearchOutcome
from providers.stackoverflow import search_stackoverflow
from providers.wikipedia import search_wikipedia
from providers.github import search_github

logger = logging.getLogger(__name__)

async def search_all(query):
    new_list = []
    down_sources = []
    list_of_sources = [ "Wikipedia",  "GitHub",  "Stack Overflow" ]
    search_all_providers = await asyncio.gather(search_wikipedia(query), search_github(query), search_stackoverflow(query), return_exceptions=True)
    for source, one_provider in zip(list_of_sources, search_all_providers):
        if isinstance(one_provider, Exception):
            logger.error("Provider %s failed: %r", source, one_provider)
            down_sources.append(source)
        else:
            new_list.extend(one_provider)
    return SearchOutcome(results=new_list, failed_sources=down_sources, total_sources=len(list_of_sources))

async def search_all_sequential(query):
    providers_results = []
    providers_results.extend(await search_wikipedia(query))
    providers_results.extend(await search_github(query))
    providers_results.extend(await search_stackoverflow(query))
    return providers_results





async def main():
    result= await search_all("python")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())