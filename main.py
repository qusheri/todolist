import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from buttons import keyboard
from config import token
import psycopg2
import config
import note_processing
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Note(StatesGroup):
    text = State()
    date = State()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):

    conn = psycopg2.connect(dbname = config.dbname_, user = config.user_, password = config.password_, host = config.host_)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE tg_id = ' + str(message.from_user.id))
    if(cursor.fetchone()[0] > 0):
        await bot.send_message(message.chat.id, "Привет! Ты уже зарегеистрирован!", reply_markup=keyboard)
    else:
        cursor.execute('INSERT INTO users VALUES (' + str(message.from_user.id) + ');')
        conn.commit()
        await bot.send_message(message.chat.id, "Привет! Давай начнем!", reply_markup=keyboard)

@dp.message(lambda message: message.text == 'Добавить заметку')
async def add_note(message: types.Message):
    note_data = []
    conn = psycopg2.connect(dbname=config.dbname_, user=config.user_, password=config.password_, host=config.host_)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM last_id')
    last_id = cursor.fetchone()[0]
    #note_id int pk, text string, user_id int, date string
    cursor.execute('INSERT INTO notes VALUES (' + str(last_id + 1) + ', \'' + text + '\', ' + str(message.from_user.id) + ', \'' + date + '\')')
    cursor.execute('UPDATE last_id SET id = ' + str(last_id + 1) + ' WHERE id = ' + str(last_id) + ';')
    conn.commit()

@dp.message(Note.text)
async def text_processing(message: types.Message, note_data, state: FSMContext):
    await state.update_data(note_text=message.text)
    await bot.send_message(message.chat.id, "Введите дату для заметки в формате дд.мм.гггг")
    await state.set_state(Note.date)

@dp.message(Note.date)
async def date_processing(message: types.Message, note_data, state: FSMContext):
    await state.update_data(note_date=message.text)
    note_data = state.get_data()
    text_data = note_data['note_text']
    date_data = note_data['note_data']


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(52)