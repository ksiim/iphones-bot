import asyncio

from models.databases import Session
from models.dbs.models import *

from sqlalchemy import distinct, insert, inspect, or_, select, text
from datetime import datetime
import pytz


class Orm:
    
    @staticmethod
    async def add_new_chat(chat_tg_id):
        async with Session() as session:
            chat = await session.execute(select(Chat).where(Chat.chat_tg_id == chat_tg_id))
            if chat is None:
                chat = Chat(chat_tg_id=chat_tg_id)
                session.add(chat)
                await session.commit()
                

    @staticmethod
    async def get_unique_tg_chat_ids():
        async with Session() as session:
            stmt = select(distinct(Chat.chat_tg_id))
            result = (await session.execute(stmt)).scalars().all()
            return result

    @staticmethod
    async def get_today_prices_by_tg_chat_id(tg_chat_id):
        async with Session() as session:
            today = datetime.now(pytz.timezone("Asia/Yekaterinburg")).date()
            query = select(Price).where(Price.chat_tg_id ==
                                        tg_chat_id).where(Price.add_date == today)
            prices = (await session.execute(query)).scalars().all()
            return prices

    @staticmethod
    async def add_price(chat_tg_id, name, price):
        async with Session() as session:
            price = Price(chat_tg_id=chat_tg_id, name=name, price=price)
            session.add(price)
            await session.commit()

    @staticmethod
    async def create_user(message):
        if await Orm.get_user_by_telegram_id(message.from_user.id) is None:
            async with Session() as session:
                user = User(
                    full_name=message.from_user.full_name,
                    telegram_id=message.from_user.id,
                    username=message.from_user.username
                )
                session.add(user)
                await session.commit()

    @staticmethod
    async def get_user_by_telegram_id(telegram_id):
        async with Session() as session:
            query = select(User).where(User.telegram_id == telegram_id)
            user = (await session.execute(query)).scalar_one_or_none()
            return user

    @staticmethod
    async def get_all_users():
        async with Session() as session:
            query = select(User)
            users = (await session.execute(query)).scalars().all()
            return users
