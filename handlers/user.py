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
        report = await generate_daily_report()
        await bot.send_message(
            chat_id=tg_chat_id,
            text=text
        )
        await bot.send_message(
            chat_id=tg_chat_id,
            text=report,
            reply_markup=kassa_keyboard
        )


@dp.message(F.text == kassa_button_text)
async def kassa_message_handler(message: Message, state: FSMContext):
    await message.answer(
        text="КАССА",
        reply_markup=kassa_keyboard
    )
    

@dp.message(F.text == revenue_button_text)
async def revenue_message_handler(message: Message, state: FSMContext):
    await message.answer(
        text="Введите сумму выручки:",
        reply_markup=cancel_keyboard
    )
    await state.set_state(RevenueForm.amount)

@dp.message(RevenueForm.amount)
async def process_revenue_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer("Сумма должна быть положительной. Попробуйте снова:")
            return
        await state.update_data(amount=amount)
        await message.answer(
            text="Введите описание",
            reply_markup=cancel_keyboard
        )
        await state.set_state(RevenueForm.description)
    except ValueError:
        await message.answer("Введите корректную сумму (целое число):")

@dp.message(RevenueForm.description)
async def process_revenue_description(message: Message, state: FSMContext):
    description = None if message.text == "/skip" else message.text
    data = await state.get_data()
    await Orm.add_cash_operation(
        user_tg_id=message.from_user.id,
        amount=data["amount"],
        description=description
    )
    await message.answer("Выручка добавлена!", reply_markup=kassa_keyboard)
    await state.clear()
    
@dp.message(F.text == exspense_button_text)
async def expense_message_handler(message: Message, state: FSMContext):
    await message.answer(
        text="Введите сумму расхода:",
        reply_markup=cancel_keyboard
    )
    await state.set_state(ExpenseForm.amount)

@dp.message(ExpenseForm.amount)
async def process_expense_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer("Сумма должна быть положительной. Попробуйте снова:")
            return
        await state.update_data(amount=-amount)  # Сохраняем как отрицательное значение
        await message.answer(
            text="Введите описание",
            reply_markup=cancel_keyboard
        )
        await state.set_state(ExpenseForm.description)
    except ValueError:
        await message.answer("Введите корректную сумму (целое число):")

@dp.message(ExpenseForm.description)
async def process_expense_description(message: Message, state: FSMContext):
    description = None if message.text == "/skip" else message.text
    data = await state.get_data()
    await Orm.add_cash_operation(
        user_tg_id=message.from_user.id,
        amount=data["amount"],
        description=description
    )
    await message.answer("Расход добавлен!", reply_markup=kassa_keyboard)
    await state.clear()
    
@dp.message(F.text == collation_button_text)
async def collation_message_handler(message: Message):
    report = await generate_daily_report()
    
    await message.answer(report, reply_markup=kassa_keyboard)

async def generate_daily_report():
    today = datetime.datetime.now(pytz.timezone("Asia/Yekaterinburg")).date()
    
    # Получаем данные
    operations = await Orm.get_today_cash_operations()
    balance_before_today = await Orm.get_balance_before_today()
    total_balance = await Orm.get_total_balance()
    
    # Вычисляем выручку и расходы за сегодня
    today_income = sum(op.amount for op in operations if op.amount > 0)
    today_expenses = abs(sum(op.amount for op in operations if op.amount < 0))
    today_balance = today_income - today_expenses
    
    # Список и количество расходов
    expense_list = [f"{abs(op.amount)} ({op.description or 'Без описания'})" for op in operations if op.amount < 0]
    expense_count = len(expense_list)
    
    # Формируем отчёт
    report = f"""
📊 Отчёт за {today}:

💵 Касса на начало дня: {balance_before_today} руб.

Выручка за сегодня: {today_income} руб.
Расходы за сегодня: {today_expenses} руб. ({expense_count} операций)

Касса за сегодня: {today_balance} руб.

💵 Касса на конец дня: {total_balance} руб.

⚠️ Список расходов:
{'; '.join(expense_list) or 'Нет операций'}
"""
    
    return report