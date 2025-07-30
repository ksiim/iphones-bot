import datetime
from aiogram import F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, FSInputFile
)

from bot import dp, bot

from models.dbs.orm import Orm
from models.dbs.models import *

from .callbacks import *
from .markups import *
from .states import *


@dp.message(Command('start'))
async def start_message_handler(message: Message, state: FSMContext):
    await state.clear()

    await Orm.create_user(message)
    await send_start_message(message)


@dp.message(F.text == 'ОТМЕНА')
async def cancel_message_handler(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text='Отменено',
        reply_markup=start_keyboard
    )


async def send_start_message(message: Message):
    await message.answer(
        text=await generate_start_text(message),
        reply_markup=start_keyboard
    )


@dp.message(F.text == add_button_text)
async def add_message_handler(message: Message, state: FSMContext):
    await state.set_state(AddState.name)

    await message.answer(
        text='Введите назначение расхода',
        reply_markup=cancel_keyboard
    )


@dp.message(AddState.name)
async def add_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text, chat_tg_id=message.chat.id)

    await message.answer(
        text=prompt_enter_expense_amount,
        reply_markup=cancel_keyboard
    )

    await state.set_state(AddState.price)


async def generate_add_price_text(name, price):
    return f'Вы хотите добавить расход:\n\n' \
        f'Назначение: {name}\n' \
        f'Сумма: {price} руб.'


@dp.message(AddState.price)
async def add_price_handler(message: Message, state: FSMContext):
    data = await state.get_data()

    try:
        price = int(message.text)
    except ValueError:
        await message.answer(
            text=prompt_enter_expense_amount,
            reply_markup=cancel_keyboard
        )
        return

    await state.update_data(price=price)

    await message.answer(
        text=await generate_add_price_text(data['name'], price),
        reply_markup=confirm_keyboard
    )


@dp.callback_query(lambda callback: callback.data.startswith('add_price'))
async def add_price_callback_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    data = await state.get_data()

    if callback.data == 'add_price:confirm':
        await Orm.add_price(data["chat_tg_id"], data['name'], int(data['price']))
        await Orm.add_new_chat(data["chat_tg_id"])

        await callback.message.answer(
            text='Расход добавлен',
            reply_markup=start_keyboard
        )

    elif callback.data == 'add_price:cancel':
        await callback.message.answer(
            text='Отменено',
            reply_markup=start_keyboard
        )

    await state.clear()


@dp.message(F.text == get_review_button_text)
async def check_message_handler(message: Message, state: FSMContext):
    text = await generate_review_text(message.chat.id)
    await message.answer(
        text=text,
    )


async def generate_review_text(tg_chat_id):
    text = f'ОТЧЕТ РАСХОДОВ ЗА СЕГОДНЯ ({datetime.datetime.now().astimezone(tz=datetime.timezone(datetime.timedelta(hours=5))).strftime("%d.%m.%Y")}):\n\n'
    prices = await Orm.get_today_prices_by_tg_chat_id(tg_chat_id)
    for price in prices:
        text += f'{price.name}: {price.price} руб.\n'
    text += f'\n\nВСЕГО: {len(prices)} шт.'
    text += f'\nСУММА: {sum([price.price for price in prices])} руб.'
    return text


async def send_daily_reviews():
    tg_chat_ids = await Orm.get_unique_tg_chat_ids()
    for tg_chat_id in tg_chat_ids:
        text = await generate_review_text(tg_chat_id)
        await bot.send_message(
            chat_id=tg_chat_id,
            text=text
        )
    