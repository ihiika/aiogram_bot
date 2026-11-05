import httpx
import asyncio

from models import SearchResult
from config import HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT


async def search_github(query: str) -> list[SearchResult]:
    params = {
        "q": query,
        "per_page": 5,
    }

    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(2, connect=HTTP_CONNECT_TIMEOUT, read=HTTP_READ_TIMEOUT)
        response = await client.get(
    "https://api.github.com/search/repositories",
        params=params,
        headers={"User-Agent": "AiogramBot/1.0 (https://github.com/ihiika/aiogram_bot)", "Accept": "application/vnd.github+json"},
        timeout=timeout,
    )
    if response.status_code != 200:
        raise RuntimeError(f"GitHub STATUS: {response.status_code} {response.text[:200]}")
    data = response.json()
    results = data.get("items")
    if results is None:
        raise RuntimeError(f"GitHub: no 'items' in response: {response.status_code} {response.text[:200]}")
    new_list = []
    for repository in results:
        title = repository.get("full_name")
        url = repository.get("html_url")
        if not url or not title:
            raise RuntimeError(f"GitHub: repository without full_name or html_url: {repository}")
        new_list.append(SearchResult(
            title,
            repository.get("description") or "no description",
            url,
            "GitHub",
        ))
    return new_list

async def main() -> None:
    results = await search_github("python")
    print(results)

if __name__ == "__main__":
    asyncio.run(main())