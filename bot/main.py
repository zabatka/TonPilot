import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_tonconnect import ATCMiddleware
from aiogram_tonconnect.tonconnect.storage.base import ATCRedisStorage

from bot.handlers import start, trade, signals, portfolio, whale
from core.config import settings
from core.db.crud import init_db


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    await init_db()

    bot = Bot(token=settings.BOT_TOKEN, parse_mode="Markdown")
    storage = RedisStorage.from_url(settings.REDIS_URL)
    dp = Dispatcher(storage=storage)

    atc_storage = ATCRedisStorage(storage.redis)
    dp.update.middleware(ATCMiddleware(atc_storage))

    dp.include_router(start.router)
    dp.include_router(trade.router)
    dp.include_router(signals.router)
    dp.include_router(portfolio.router)
    dp.include_router(whale.router)

    logging.info("TonPilot bot starting...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
