import httpx
import asyncio

from models import SearchResult


async def search_github(query):
    params = {
        "q": query,
        "per_page": 5,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
        "https://api.github.com/search/repositories",
        params=params,
        headers={"User-Agent": "AiogramBot/1.0 (https://github.com/ihiika/aiogram_bot)", "Accept": "application/vnd.github+json"},
    )
    if response.status_code != 200:
        raise RuntimeError(f"GITHUB STATUS: {response.status_code}  {response.text[:200]}")
    data = response.json()
    results = data["items"]

    new_list = []
    for repository in results:
        new_list.append(SearchResult(
            repository["full_name"],
            repository["description"] or "no description",
            repository["html_url"],
            "GitHub",
        ))
    return new_list

async def main():
    results = await search_github("ijfefwe8d3m28423")
    print(results)

if __name__ == "__main__":
    asyncio.run(main())