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
        outcome = await search_all(query)
    except Exception:
        logger.exception("search for all sources failed for query=%r", query)
        return await message.reply("Something went wrong")
    list_of_records = []
    answers_for_failed_sources = ""
    if outcome.results:
        for item in outcome.results:
            list_of_records.append(f"{item.title}: {item.description} \nLink: {item.url} \nSource: {item.source}\n")
    answers_for_records = "\n".join(list_of_records)

    if outcome.failed_sources:
        answers_for_failed_sources = "Unavailable: " + ", ".join(outcome.failed_sources)

    if outcome.all_failed:
        return await message.reply("All sources failed. Try again later")
    elif not outcome.results and outcome.failed_sources:
        await message.reply(f"No results from the available sources. {answers_for_failed_sources}")
    elif not outcome.results:
        return await message.reply("No results found")
    return await message.reply(f"{answers_for_records} \n\n{answers_for_failed_sources}")


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