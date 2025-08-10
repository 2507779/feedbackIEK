import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Admin User IDs
ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# Database path
DATABASE_PATH = os.getenv('DATABASE_PATH', 'feedback.db')

# Категории обратной связи
FEEDBACK_CATEGORIES = {
    "tpa": "Цех термопластавтоматов (ТПА)",
    "aluminum": "Цех литья алюминия", 
    "assembly": "Монтаж, упаковка, сборка светильников",
    "logistics": "Логистика и склад",
    "hr": "HR и кадры",
    "general": "Общие вопросы"
}

# Типы обратной связи
FEEDBACK_TYPES = {
    "complaint": "ЖАЛОБА",
    "suggestion": "ПРЕДЛОЖЕНИЕ"
}

# Статусы заявок
FEEDBACK_STATUSES = {
    "new": "Новая",
    "in_progress": "В работе", 
    "closed": "Закрыта"
}

# Проверка обязательных переменных
if not BOT_TOKEN:
    if not os.getenv('TESTING'):
        raise ValueError("BOT_TOKEN не установлен в переменных окружения")

if not ADMIN_IDS:
    if not os.getenv('TESTING'):
        raise ValueError("ADMIN_IDS не установлены в переменных окружения")

