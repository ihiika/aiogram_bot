import httpx
import html
import asyncio

from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    description: str
    url: str
    source: str

def clean_snippet(text):
    text = text.replace('<span class="searchmatch">', "")
    text = text.replace('</span>', "")
    text = html.unescape(text)
    return text


async def search_wikipedia(query):
    params = {
        'action': "query",  # выбирает тип, чтение а не редактирование например
        'list': "search",  # список результатов поиска
        'srsearch': query,  # сама строка
        'srlimit': "5",  # ограничение запросов
        'format': "json",  # нужен json
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("https://en.wikipedia.org/w/api.php", params=params, headers={"User-Agent": "aiogram_bot/1.0"})
    if response.status_code != 200:
        raise RuntimeError(f"WIKI STATUS: {response.status_code}")
    data = response.json()
    if data.get('error'):
        raise RuntimeError(data['error']['info'])
    results = data['query']['search']

    new_list = []
    for page in results:
        new_list.append(SearchResult(
            page["title"],
            clean_snippet(page["snippet"]),
            f'https://en.wikipedia.org/?curid={page['pageid']}',
            "Wikipedia"
        ))
    return new_list

async def main():
    result = await search_wikipedia("GIT")
    print(result)



asyncio.run(main())


