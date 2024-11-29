from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# Клавиатура с кнопкой /start
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")],  # Кнопка с текстом команды /start
    ],
    resize_keyboard=True  # Делаем кнопки компактными
)

counter_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Шевеляшка", callback_data="increment"),
            InlineKeyboardButton(text="Показать", callback_data="show"),
        ]
    ]
)
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")],
        [KeyboardButton(text="/clear")],
    ],
    resize_keyboard=True  # Уменьшает размер кнопок
)