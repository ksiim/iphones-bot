import asyncio

from bot import dp, bot

import logging

import handlers

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from models.databases import create_database


logging.basicConfig(level=logging.INFO)

async def main():
    await create_database()
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(handlers.send_daily_reviews, 'interval', seconds=5)
    scheduler.add_job(handlers.send_daily_reviews, 'cron', hour=16, minute=35)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())