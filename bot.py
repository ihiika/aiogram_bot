import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello, Im aiogram bot ")

@dp.message(F.text)
async def any_text(message: Message) -> None:
    await message.answer(f"You were looking for: {message.text}")

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