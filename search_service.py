import asyncio

from providers_wikipedia import search_wikipedia
from providers_github import search_github

async def search_all(query):
    results_wikipedia = await search_wikipedia(query)
    results_github = await search_github(query)
    return results_wikipedia + results_github


async def main():
    result= await search_all("python")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())