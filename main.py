import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import BOT_TOKEN, DATABASE_PATH
from database import Database
from handlers import router as main_router
from admin_handlers import router as admin_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    
    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)
    
    # Инициализация диспетчера
    dp = Dispatcher()
    
    # Инициализация базы данных
    db = Database(DATABASE_PATH)
    await db.init_db()
    
    # Регистрация роутеров
    dp.include_router(main_router)
    dp.include_router(admin_router)
    
    # Middleware для передачи базы данных в хендлеры
    @dp.message.middleware()
    @dp.callback_query.middleware()
    async def db_middleware(handler, event, data):
        data['db'] = db
        return await handler(event, data)
    
    logger.info("Бот запущен")
    
    try:
        # Запуск бота
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

