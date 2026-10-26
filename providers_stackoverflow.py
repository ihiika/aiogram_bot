import asyncio
import httpx
import html

from models import SearchResult

async def search_stackoverflow(query):
    params = {
        'site': 'stackoverflow',
        'q': query,
        'pagesize': 5,
        'sort': 'relevance',
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.stackexchange.com/2.3/search/advanced",
        params=params, headers={"User-Agent": "AiogramBot/1.0 (https://github.com/ihiika/aiogram_bot)"})

    if response.status_code != 200:
        raise RuntimeError(f"StackOverFlow STATUS: {response.status_code}  {response.text[:200]}")
    data = response.json()
    #print(data.keys())  # ключи верхнего уровня
    #print(data["items"][0].keys())  # ключи одного элемента
    results = data['items']

    new_list = []

    for result in results:
        new_list.append(SearchResult(html.unescape(result["title"]),  f"Score: {result['score']}", result["link"], "Stackoverflow"))

    return new_list

async def main():
    results = await search_stackoverflow("git")
    print(results)

if __name__ == "__main__":
    asyncio.run(main())