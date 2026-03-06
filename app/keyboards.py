from aiogram.types import ReplyKeyboardMarkup, keyboard_button, KeyboardButton

main=ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Каталог")],
    [KeyboardButton(text="Начинки"), KeyboardButton(text="Вес")],
    [KeyboardButton(text="Контакты")]
])

