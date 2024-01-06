import asyncio
import logging
import time
import schedule

from aiohttp import ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from DataBase import DataBase  # my module
from configs import BOT_TOKEN, API_URL, API_KEY
from start_message import START_MESSAGE_1, START_MESSAGE_2, START_MESSAGE_3

headers = {"x-api-key": API_KEY}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
tg_db = DataBase("telegram.db")


async def get_cat(url, headers):
    async with ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            cat_data = await response.json()
            return cat_data[0]["url"]


@dp.message(CommandStart())
async def start(message: types.Message):
    id = f"{message.chat.id}"
    start_db = DataBase("telegram.db")
    start_db.insert("users", ("chat_id",), (id,))
    start_db.disconnect()

    await message.answer(START_MESSAGE_1)
    await message.answer(START_MESSAGE_2)
    await message.answer(START_MESSAGE_3)


@dp.message(Command("cat"))
async def send_cat(message: types.Message):
    cat_url = await get_cat(API_URL, headers)
    await bot.send_photo(message.chat.id, photo=cat_url)


@dp.message(Command("admin_cute"))
async def cute_message(message: types.Message):
    cute_db = DataBase("telegram.db")
    req = """WHERE phrases_id = (
            SELECT abs(random()) % (SELECT max(phrases_id) + 1 
            FROM phrases) + 1) 
    AND NOT EXISTS (
        SELECT 1
        FROM history h
        JOIN users u USING (users_id)
        WHERE h.phrases_id = p.phrases_id
        AND u.users_id = h.users_id)"""

    users = cute_db.get("users",("users_id","chat_id",))

    for user in users:
        res_break = True
        while res_break:
            try:
                phrase = cute_db.get(
                    "phrases p", ("p.phrases_id, p.text",), add_request=req)[0]
                cute_db.insert(
                    "history", ("phrases_id", "users_id"), (phrase[0], user[0]))

                await bot.send_message(chat_id=user[1], text=phrase[1])
                res_break = False
            except Exception as e:
                print(f"Error sending message")
                time.sleep(2)
                continue
    cute_db.disconnect()


@dp.message(Command("nonstop"))
async def nonstop_cat(message: types.Message):
    while True:
        await cute_message(message)
        time.sleep(1)


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
