import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from config import token
import psycopg2
import config

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    conn = psycopg2.connect(dbname = config.dbname_, user = config.user_, password = config.password_, host = config.host_)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE tg_id = ' + str(message.from_user.id))
    if(cursor.fetchone()[0] > 0):
        await bot.send_message(message.chat.id, "Привет! Ты уже зарегеистрирован!")
    else:
        cursor.execute('INSERT INTO users VALUES (' + str(message.from_user.id) + ');')
        conn.commit()
        await bot.send_message(message.chat.id, "Привет! Давай начнем!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(52)