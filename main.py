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
from datetime import datetime, timedelta
import pytz
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Note(StatesGroup):
    text = State()
    date = State()
class TimeZone(StatesGroup):
    timezone = State()

@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    conn = psycopg2.connect(dbname = config.dbname_, user = config.user_, password = config.password_, host = config.host_)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE tg_id = ' + str(message.from_user.id))
    if(cursor.fetchone()[0] > 0):
        await bot.send_message(message.chat.id, "Привет! Ты уже зарегеистрирован.", reply_markup=keyboard)
    else:
        await bot.send_message(message.chat.id, "Привет! Давай начнем.\nВведи свой часовой пояс относительно МСК")
        await state.set_state(TimeZone.timezone)

@dp.message(TimeZone.timezone)
async def start_proceed(message: types.Message, state: FSMContext):
    conn = psycopg2.connect(dbname = config.dbname_, user = config.user_, password = config.password_, host = config.host_)
    cursor = conn.cursor()
    await state.update_data(timezone = message.text)
    data = await state.get_data()
    time_zone = data['timezone']
    if not time_zone.isdigit():
        await cmd_start(message)
    cursor.execute('INSERT INTO users VALUES (' + str(message.from_user.id) + ', ' + str(int(time_zone) + 3) + ');')
    conn.commit()
    await bot.send_message(message.chat.id, "Готово! Теперь ты зарегестрирован.", reply_markup=keyboard)

@dp.message(lambda message: message.text == 'Добавить заметку')
async def add_note(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Введите текст заметки")
    await state.set_state(Note.text)
@dp.message(Note.text)
async def text_processing(message: types.Message, state: FSMContext):
    await state.update_data(note_text=message.text)
    await bot.send_message(message.chat.id, "Введите дату для заметки в формате 'гггг-мм-дд чч:мм:сс'")
    await state.set_state(Note.date)

@dp.message(Note.date)
async def date_processing(message: types.Message, state: FSMContext):
    await state.update_data(note_date=message.text)
    note_data = await state.get_data()
    text_data = note_data['note_text']
    date_data = note_data['note_date']
    await save_note(text_data, date_data, message.from_user.id)

async def is_valid_date(timestamp_str):
    try:
        datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False

async def save_note(text, date, user_id):
    conn = psycopg2.connect(dbname=config.dbname_, user=config.user_, password=config.password_, host=config.host_)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM last_id')
    last_id = cursor.fetchone()[0]
    #note_id int pk, text string, user_id int, date string
    if not await is_valid_date(date):
        await bot.send_message(user_id, "Неверный формат, попробуй снова")
    cursor.execute('INSERT INTO notes VALUES (' + str(last_id + 1) + ', \'' + text + '\', ' + str(user_id) + ', \'' + date + '\')')
    cursor.execute('UPDATE last_id SET id = ' + str(last_id + 1) + ' WHERE id = ' + str(last_id) + ';')
    conn.commit()
    await bot.send_message(user_id, "Заметка добавлена")
    await schedule_message(user_id, text, date, last_id + 1)


def add_timezone(utc_time_str, offset_hours):
    try:
        utc_time = datetime.strptime(utc_time_str.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        utc_time = utc_time.replace(tzinfo=pytz.utc)
        new_time = utc_time - timedelta(hours=offset_hours)
        return new_time
    except ValueError:
        return None

async def schedule_message(user_id, message, send_time, note_id):
    cursor = psycopg2.connect(dbname=config.dbname_, user=config.user_, password=config.password_, host=config.host_).cursor()
    cursor.execute('SELECT * FROM users WHERE tg_id = ' + str(user_id))
    user_tz = cursor.fetchone()[1]
    naive_time = datetime.strptime(send_time, '%Y-%m-%d %H:%M:%S')
    utc_time = naive_time.replace(tzinfo=pytz.utc)
    now = datetime.now(pytz.utc)
    utc_time = add_timezone(utc_time, user_tz)
    delay = (utc_time - now).total_seconds()
    print('заметка с id ' + str(note_id) + ' будет отправлена через ' + str(delay))
    if delay > 0:
        await asyncio.sleep(delay)
    await bot.send_message(user_id, message)



async def main():
    conn = psycopg2.connect(dbname=config.dbname_, user=config.user_, password=config.password_, host=config.host_)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE date < NOW()')
    conn.commit()
    cursor.execute('SELECT * FROM notes')
    notes = cursor.fetchall()
    tasks = []
    for note in notes:
        tasks.append(schedule_message(note[2], note[1], note[3].strftime('%Y-%m-%d %H:%M:%S'), note[0]))
    await asyncio.gather(*tasks)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(52)