import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

from handlers import admin, user

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()
bot = Bot(token=TOKEN)

admin.register_handlers_admin(dp)
user.register_handlers_user(dp)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
