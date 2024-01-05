import asyncio
import logging


from aiohttp import ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from DataBase import DataBase  # my module
from configs import BOT_TOKEN, API_URL, API_KEY

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
    tg_db = DataBase("telegram.db")
    tg_db.insert("users", ("chat_id",), (id,))
    tg_db.disconnect()
    
    await message.answer("Hello, my command is /cat")


@dp.message(Command("cat"))
async def send_cat(message: types.Message):
    cat_url = await get_cat(API_URL, headers)
    await bot.send_photo(message.chat.id, photo=cat_url)


@dp.message(Command("cute"))
async def cute_message(message: types.Message):
    req = '''WHERE phrases_id = (
            SELECT abs(random()) % (SELECT max(phrases_id) + 1 
            FROM phrases) + 1) 
    AND NOT EXISTS (
        SELECT 1
        FROM history h
        JOIN users u USING (users_id)
        WHERE h.phrases_id = p.phrases_id
        AND u.users_id = h.users_id
                    )'''    
                         
    users = tg_db.get("users", ('users_id', 'chat_id',),)
    for user in users:
        phrase = tg_db.get("phrases p", ('p.phrases_id, p.text',), add_request=req)
        tg_db.insert("history", ("phrases_id", "users_id"), (phrase[0], user[0]))
        
        await bot.send_message(chat_id=user[1], text=phrase[1])
    tg_db.disconnect()    
        
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
