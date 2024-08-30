from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
button1 = KeyboardButton(text="Добавить заметку")
button2 = KeyboardButton(text="Посмотреть все мои заметки")
button3 = KeyboardButton(text="Ближайшее запланированное дело")
keyboard = ReplyKeyboardMarkup(keyboard = [[button1, button2, button3]], resize_keyboard=True)