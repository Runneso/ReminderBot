from asyncio import run
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, \
#     InlineKeyboardButton,Message
from os import getenv
from dotenv import load_dotenv
from threading import Timer

load_dotenv()
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def start(message: types.Message):
    print(message.text)


async def main() -> None:
    bot = Bot(token=TELEGRAM_TOKEN)
    await dp.start_polling(bot)


if __name__ == '__main__':
    run(main())
