import asyncio
from enum import nonmember

import httpx
import html

from models import SearchResult
from config import HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT

async def search_stackoverflow(query: str) -> list[SearchResult]:
    params = {
        'site': 'stackoverflow',
        'q': query,
        'pagesize': 5,
        'sort': 'relevance',
    }
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(2, connect=HTTP_CONNECT_TIMEOUT, read=HTTP_READ_TIMEOUT)
        response = await client.get("https://api.stackexchange.com/2.3/search/advanced",
        timeout=timeout,
        params=params, headers={"User-Agent": "AiogramBot/1.0 (https://github.com/ihiika/aiogram_bot)"})

    if response.status_code != 200:
        raise RuntimeError(f"StackOverFlow status: {response.status_code}  {response.text[:200]}")
    data = response.json()
    results = data.get("items")
    if results is None:
        raise RuntimeError(f"Stack Overflow: no 'items' in response: {response.status_code} {response.text[:200]}")
    new_list = []
    for result in results:
        title = result.get("title")
        link = result.get("link")
        if not title or not link:
            raise RuntimeError(f"Stack OverFlow: result is without title or link {result}")
        answer_count = result.get("answer_count")
        accepted_answer_id = result.get("accepted_answer_id")
        has_accepted = accepted_answer_id is not None
        extras = []
        extras.append(f"Score: {result.get('score', 0)}")
        if answer_count is not None:
            extras.append(f"Answers: {answer_count}")
        if has_accepted:
            extras.append("✅")
        extra_info = " · ".join(extras)
        new_list.append(SearchResult(title=html.unescape(title), description=extra_info, url=link, source="Stack Overflow"))

    return new_list

async def main() -> None:
    results = await search_stackoverflow("git")
    print(results)

if __name__ == "__main__":
    asyncio.run(main())