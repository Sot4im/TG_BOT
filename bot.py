import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router as main_router
from app.order_handler import router as order_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    print("🚀 Бот запускается...")

    dp.include_router(order_router)
    dp.include_router(main_router)


    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен") 