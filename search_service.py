import asyncio

from providers_stackoverflow import search_stackoverflow
from providers_wikipedia import search_wikipedia
from providers_github import search_github

async def search_all(query):
    new_list = []
    search_all_providers = await asyncio.gather(search_wikipedia(query), search_github(query), search_stackoverflow(query))
    for one_provider in search_all_providers:
        new_list.extend(one_provider)
    return new_list

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