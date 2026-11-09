import httpx
import html
import asyncio

from models import SearchResult
from config import HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT



def clean_snippet(text: str) -> str:
    text = text.replace('<span class="searchmatch">', "")
    text = text.replace('</span>', "")
    text = html.unescape(text)
    return text


async def search_wikipedia(query: str) -> list[SearchResult]:
    params = {
        'action': "query",  # выбирает тип, чтение а не редактирование например
        'list': "search",  # список результатов поиска
        'srsearch': query,  # сама строка
        'srlimit': "5",  # ограничение запросов
        'format': "json",  # нужен json
    }
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(2, connect=HTTP_CONNECT_TIMEOUT, read=HTTP_READ_TIMEOUT)
        response = await client.get("https://en.wikipedia.org/w/api.php", params=params, headers={"User-Agent": "AiogramBot/1.0 (https://github.com/ihiika/aiogram_bot)"}, timeout=timeout)
    if response.status_code != 200:
        raise RuntimeError(f"Wikipedia status: {response.status_code}")
    data = response.json()
    error = data.get("error")
    if error:
        info = error.get("info")
        if info:
            raise RuntimeError(f"Wikipedia error: {info}")
        raise RuntimeError(f"Wikipedia error without info: {error}")
    query_part = data.get("query")
    if query_part is None:
        raise RuntimeError(f"Wikipedia: no 'query' in response: {response.text[:200]}")
    results = query_part.get("search")
    if results is None:
        raise RuntimeError(f"Wikipedia: no 'search' in 'query': {response.text[:200]}")

    new_list = []
    for page in results:
        title = page.get("title")
        snippet = page.get("snippet", "No snippet")
        cleaned_snippet = clean_snippet(snippet)
        page_id = page.get("pageid")
        if not title or not page_id:
            raise RuntimeError(f"Wikipedia: no 'title' or 'pageid' {response.text[:200]}")
        new_list.append(SearchResult(
            title = title,
            description = cleaned_snippet,
            url = f'https://en.wikipedia.org/?curid={page_id}',
            source = "Wikipedia",
        ))
    return new_list

async def main() -> None:
    result = await search_wikipedia("GIT")
    print(result)

if __name__ == '__main__':
    asyncio.run(main())


