from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from bot import bot

from .callbacks import *


async def generate_start_text(message):
    return f"Привет, {message.from_user.full_name}! Я - бот"


add_button_text = 'ДОБАВИТЬ РАСХОД'
get_review_button_text = 'СВЕРКА ДНЯ'
kassa_button_text = 'КАССА'
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=add_button_text)
        ],
        [
            KeyboardButton(text=get_review_button_text)
        ],
        [
            KeyboardButton(text=kassa_button_text)
        ]
    ],
    resize_keyboard=True
)

cancel_button = KeyboardButton(text='ОТМЕНА')

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            cancel_button
        ]
    ],
    resize_keyboard=True
)

revenue_button_text = 'ВЫРУЧКА'
exspense_button_text = 'РАСХОД'
collation_button_text = 'СВЕРКА'

kassa_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=revenue_button_text),
        ],
        [
            KeyboardButton(text=exspense_button_text),
        ],
        [
            KeyboardButton(text=collation_button_text),
        ],
        [
            cancel_button
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
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
