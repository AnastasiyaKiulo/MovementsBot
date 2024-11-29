from aiogram import Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from kb import start_keyboard, counter_keyboard
from db import increment_counter, add_log_entry, get_counter_and_logs, clear_user_data
from datetime import datetime

router = Router()

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(
        "Выберите действие:",
        reply_markup=counter_keyboard
    )

@router.message(Command("clear"))
async def clear_handler(msg: Message):
    user_id = msg.from_user.id
    clear_user_data(user_id)  # Очищаем данные только для текущего пользователя
    await msg.answer("Ваши данные были очищены.")

@router.callback_query()
async def callback_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    if callback.data == "increment":
        # Увеличиваем счетчик
        new_value = increment_counter(user_id)
        await callback.message.edit_text(
            text=f"Счетчик увеличен! Новое значение: {new_value}",
            reply_markup=counter_keyboard
        )
        await callback.answer()

    elif callback.data == "show":
        # Показываем текущее значение и лог
        # add_log_entry(user_id, '2024-11-28 12:16:00')
        current_value, formatted_logs = get_counter_and_logs(user_id)
        if formatted_logs:
            response = f"Текущее значение счетчика: {current_value}\n\nЛоги событий:\n{formatted_logs}"
        else:
            response = f"Текущее значение счетчика: {current_value}\n\nНет записей."

        await callback.message.edit_text(
            text=response,
            reply_markup=counter_keyboard
        )
        await callback.answer()

# @router.message()
# async def message_handler(msg: Message):
#     await msg.answer(f"Твой ID: {msg.from_user.id}")