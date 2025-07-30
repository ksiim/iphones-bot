from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from bot import bot

from .callbacks import *


async def generate_start_text(message):
    return f"Привет, {message.from_user.full_name}! Я - бот"


add_button_text = 'ДОБАВИТЬ РАСХОД'
get_review_button_text = 'СВЕРКА ДНЯ'
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=add_button_text)
        ],
        [
            KeyboardButton(text=get_review_button_text)
        ]
    ],
    resize_keyboard=True
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='ОТМЕНА')
        ]
    ],
    resize_keyboard=True
)


prompt_enter_expense_amount = 'Введите сумму (целое число) расхода в рублях'

confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✅ Да',
                callback_data="add_price:confirm"
            ),
        ],
        [
            InlineKeyboardButton(
                text='❌ Нет',
                callback_data="add_price:cancel"
            )
        ]
    ]
)
