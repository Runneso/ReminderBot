import datetime
from asyncio import run, sleep, create_task
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv
from dotenv import load_dotenv
from phrases import phrases
from keyboards import main_keyboard, change_timezone_keyboard, clear_keyboard, none_keyboard, UTC

load_dotenv()
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=TELEGRAM_TOKEN)
timezone = datetime.timezone(offset=datetime.timedelta(hours=0))
add_task_array = list()
tasks = list()


async def remind(delta: int, chat_id: int, event_title: str, file_id: str) -> None:
    await sleep(delta)
    if file_id != "None":
        await bot.send_message(chat_id=chat_id, text="REMIND!")
        await bot.send_photo(chat_id=chat_id, photo=file_id,
                             caption=event_title + " " + str(datetime.datetime.now().date()))
    else:
        await bot.send_message(chat_id=chat_id, text="REMIND!")
        await bot.send_message(chat_id=chat_id, text=event_title + " " + str(datetime.datetime.now().date()))


class States(StatesGroup):
    set_state = State()
    add_task_1 = State()
    add_task_2 = State()
    add_task_3 = State()
    remove_task = State()
    change_timezone = State()


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    text = phrases.start
    await bot.send_message(chat_id=chat_id, text=text.format(message.from_user.username), reply_markup=main_keyboard)
    await state.set_state(States.set_state)


@dp.message(States.set_state)
async def set_state(message: types.Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    variants = {"➕ Add task.", "➖ Remove task.", "🕐 Change timezone task."}
    if message.text not in variants:
        await state.set_state(States.set_state)
        await bot.send_message(chat_id=chat_id, text=phrases.incorrect_variant, reply_markup=main_keyboard)
    else:
        match message.text:
            case "➕ Add task.":
                await state.set_state(States.add_task_1)
                await bot.send_message(chat_id=chat_id, text=phrases.add_task_1, reply_markup=clear_keyboard)
            case "➖ Remove task.":
                if tasks:
                    await state.set_state(States.remove_task)
                    current_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[])
                    for index in range(len(tasks)):
                        current_keyboard.keyboard.append(
                            [types.KeyboardButton(text=f"{index + 1}. {tasks[index].get_name()}")])
                    await bot.send_message(chat_id=chat_id, text=phrases.remove_task, reply_markup=current_keyboard)
                else:
                    await bot.send_message(chat_id=chat_id, text=phrases.no_tasks, reply_markup=main_keyboard)
                    await state.set_state(States.set_state)
            case "🕐 Change timezone task.":
                await state.set_state(States.change_timezone)
                await bot.send_message(chat_id=chat_id, text=phrases.choose_timezone,
                                       reply_markup=change_timezone_keyboard)


@dp.message(States.add_task_1)
async def add_task_1(message: types.Message, state: FSMContext) -> None:
    global timezone
    chat_id = message.chat.id
    try:
        reminder_time = datetime.datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone)
        current_time = datetime.datetime.now(tz=timezone)
        delta = reminder_time - current_time
        if delta.total_seconds() <= 0:
            await bot.send_message(chat_id=chat_id, text=phrases.past_date, reply_markup=clear_keyboard)
            await state.set_state(States.add_task_1)
        else:
            add_task_array.append(delta.total_seconds())
            await bot.send_message(chat_id=chat_id, text=phrases.add_task_2, reply_markup=clear_keyboard)
            await state.set_state(States.add_task_2)

    except ValueError:
        await bot.send_message(chat_id=chat_id, text=phrases.incorrect_variant, reply_markup=clear_keyboard)
        await state.set_state(States.add_task_1)


@dp.message(States.add_task_2)
async def add_task_2(message: types.Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    if message.content_type == types.ContentType.TEXT:
        add_task_array.append(message.text)
        await bot.send_message(chat_id=chat_id, text=phrases.add_task_3, reply_markup=none_keyboard)
        await state.set_state(States.add_task_3)
    else:
        await bot.send_message(chat_id=chat_id, text=phrases.incorrect_variant, reply_markup=clear_keyboard)
        await state.set_state(States.add_task_2)


@dp.message(States.add_task_3)
async def add_task_3(image: types.Message, state: FSMContext) -> None:
    global add_task_array
    chat_id = image.chat.id
    if image.content_type == types.ContentType.PHOTO:
        add_task_array.append(image.photo[3].file_id)
        delta, chat_id, event_title, file_id = int(add_task_array[0]), chat_id, add_task_array[1], add_task_array[2]
        add_task_array = list()
        task = create_task(remind(delta=int(delta), chat_id=chat_id, event_title=event_title, file_id=file_id),
                           name=event_title)
        tasks.append(task)
        await bot.send_message(chat_id=chat_id, text=phrases.correct_task_add, reply_markup=main_keyboard)
        await state.set_state(States.set_state)
    elif image.text == "None":
        add_task_array.append("None")
        delta, chat_id, event_title, file_id = int(add_task_array[0]), chat_id, add_task_array[1], add_task_array[2]
        add_task_array = list()
        task = create_task(remind(delta=int(delta), chat_id=chat_id, event_title=event_title, file_id=file_id),
                           name=event_title)
        tasks.append(task)
        await bot.send_message(chat_id=chat_id, text=phrases.correct_task_add, reply_markup=main_keyboard)
        await state.set_state(States.set_state)
    else:
        await bot.send_message(chat_id=chat_id, text=phrases.incorrect_variant, reply_markup=none_keyboard)
        await state.set_state(States.add_task_3)


@dp.message(States.remove_task)
async def remove_task(message: types.Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    index = message.text.split()[0][:-1]
    if index.isdigit() and 0 <= int(index) - 1 < len(tasks):
        tasks[int(index) - 1].cancel()
        del tasks[int(index) - 1]
        await bot.send_message(chat_id=chat_id, text=phrases.correct_task_remove, reply_markup=main_keyboard)
        await state.set_state(States.set_state)

    else:
        await bot.send_message(chat_id=chat_id, text=phrases.incorrect_variant)
        await state.set_state(States.remove_task)


@dp.message(States.change_timezone)
async def change_timezone(message: types.Message, state: FSMContext) -> None:
    global timezone
    chat_id = message.chat.id
    variants = set([time[0] for time in UTC])
    if message.text not in variants:
        await state.set_state(States.change_timezone)
        await bot.send_message(chat_id=chat_id, text=phrases.incorrect_variant, reply_markup=change_timezone_keyboard)
    else:
        hours = int(message.text.split()[1])
        timezone = datetime.timezone(offset=datetime.timedelta(hours=hours))
        await state.set_state(States.set_state)
        await bot.send_message(chat_id=chat_id, text=phrases.correct_timezone_change, reply_markup=main_keyboard)


@dp.message()
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    run(main())
