import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from search_service import search_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer("Hello, Im aiogram bot ")

@dp.message(F.text)
async def any_text(message: Message):
    query = message.text.strip()
    if not query:
        return await message.reply("The requested text is empty")
    await message.answer(f"You were looking for: {query}")
    try:
        results = await search_all(query)
    except Exception as e:
        logger.exception("Wikipedia search failed for query=%r", query)
        return await message.reply("Something went wrong")
    lines = []
    if results:
        for item in results:
            lines.append(f"{item.title}: {item.description} \nLink: {item.url} \nSource: {item.source}\n")
        text = "\n".join(lines)
        return await message.answer(text)
    return await message.reply("No results found")




@dp.message()
async def not_text(message: Message) -> None:
    await message.answer("Invalid input")



async def main():
    load_dotenv("token.env")
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not provided")
    bot = Bot(token=token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())