import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router as main_router
from app.order_handler import router as order_router
from app.database import db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    print("🚀 Бот запускается...")
    print("✅ База данных SQLite готова")

    # Подключаем роутеры
    dp.include_router(order_router)
    dp.include_router(main_router)

    print("✅ Бот готов к работе!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")