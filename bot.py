import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from search_service import search_all
from text_divider import split_records

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
async def any_text(message: Message) -> None:
    query = message.text.strip()
    if not query:
        await message.reply("The requested text is empty")
        return
    try:
        outcome = await search_all(query)
    except Exception:
        logger.exception("search for all sources failed for query=%r", query)
        await message.reply("Something went wrong")
        return
    list_of_records = []
    answers_for_failed_sources = ""
    if outcome.results:
        for item in outcome.results:
            list_of_records.append(f"\n{item.title}: {item.description} \nLink: {item.url} \nSource: {item.source}\n")
    answers_for_records = split_records(list_of_records)
    if outcome.failed_sources:
        answers_for_failed_sources = "Unavailable: " + ", ".join(outcome.failed_sources)
    if outcome.all_failed:
        await message.reply("All sources failed. Try again later")
        return
    elif not outcome.results and outcome.failed_sources:
        await message.reply(f"No results from the available sources. {answers_for_failed_sources}")
        return
    elif not outcome.results:
        await message.reply("No results found")
        return
    for part in answers_for_records:
        await message.reply(part)
    if answers_for_failed_sources:
        await message.reply(answers_for_failed_sources)

@dp.message()
async def not_text(message: Message) -> None:
    await message.answer("Invalid input")



async def main() -> None:
    load_dotenv("token.env")
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not provided")
    bot = Bot(token=token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())