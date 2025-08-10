#!/usr/bin/env python3
"""
Тестовый скрипт для проверки основных функций бота
"""

import asyncio
import os
import sys

# Устанавливаем переменные окружения для тестирования ПЕРЕД импортом
os.environ['TESTING'] = '1'
os.environ.setdefault('BOT_TOKEN', 'test_token')
os.environ.setdefault('ADMIN_IDS', '123456789')

from database import Database
from config import FEEDBACK_CATEGORIES, FEEDBACK_TYPES

async def test_database():
    """Тестирование базы данных"""
    print("🔍 Тестирование базы данных...")
    
    # Создаем тестовую базу
    db = Database("test_feedback.db")
    
    try:
        # Инициализация
        await db.init_db()
        print("✅ База данных инициализирована")
        
        # Добавление пользователя
        await db.add_user(
            user_id=123456789,
            username="test_user",
            first_name="Тест",
            last_name="Пользователь"
        )
        print("✅ Пользователь добавлен")
        
        # Установка админских прав
        await db.set_admin(123456789, True)
        is_admin = await db.is_admin(123456789)
        assert is_admin, "Ошибка установки админских прав"
        print("✅ Админские права установлены")
        
        # Добавление заявки
        feedback_id = await db.add_feedback(
            user_id=123456789,
            username="test_user",
            first_name="Тест",
            last_name="Пользователь",
            category="Цех термопластавтоматов (ТПА)",
            feedback_type="complaint",
            message="Тестовая жалоба на работу оборудования",
            is_anonymous=False
        )
        print(f"✅ Заявка #{feedback_id} добавлена")
        
        # Получение заявки
        feedback = await db.get_feedback_by_id(feedback_id)
        assert feedback is not None, "Ошибка получения заявки"
        print("✅ Заявка получена")
        
        # Обновление статуса
        await db.update_feedback_status(
            feedback_id=feedback_id,
            status="in_progress",
            admin_id=123456789
        )
        print("✅ Статус заявки обновлен")
        
        # Получение статистики
        stats = await db.get_stats()
        assert stats['total'] > 0, "Ошибка получения статистики"
        print(f"✅ Статистика получена: {stats}")
        
        # Получение категорий
        categories = await db.get_categories()
        assert len(categories) > 0, "Ошибка получения категорий"
        print(f"✅ Категории получены: {len(categories)} шт.")
        
        print("🎉 Все тесты базы данных прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования базы данных: {e}")
        return False
    
    finally:
        # Удаляем тестовую базу
        if os.path.exists("test_feedback.db"):
            os.remove("test_feedback.db")
    
    return True

def test_config():
    """Тестирование конфигурации"""
    print("🔍 Тестирование конфигурации...")
    
    try:
        # Проверяем категории
        assert len(FEEDBACK_CATEGORIES) > 0, "Категории не определены"
        print(f"✅ Категории: {len(FEEDBACK_CATEGORIES)} шт.")
        
        # Проверяем типы
        assert len(FEEDBACK_TYPES) > 0, "Типы обратной связи не определены"
        print(f"✅ Типы обратной связи: {len(FEEDBACK_TYPES)} шт.")
        
        # Проверяем обязательные переменные (если установлены)
        if os.getenv('BOT_TOKEN'):
            print("✅ BOT_TOKEN установлен")
        else:
            print("⚠️ BOT_TOKEN не установлен (нормально для тестирования)")
        
        if os.getenv('ADMIN_IDS'):
            print("✅ ADMIN_IDS установлены")
        else:
            print("⚠️ ADMIN_IDS не установлены (нормально для тестирования)")
        
        print("🎉 Тестирование конфигурации завершено!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования конфигурации: {e}")
        return False

def test_imports():
    """Тестирование импортов"""
    print("🔍 Тестирование импортов...")
    
    try:
        # Основные модули
        import main
        print("✅ main.py импортирован")
        
        import handlers
        print("✅ handlers.py импортирован")
        
        import admin_handlers
        print("✅ admin_handlers.py импортирован")
        
        import keyboards
        print("✅ keyboards.py импортирован")
        
        import database
        print("✅ database.py импортирован")
        
        import config
        print("✅ config.py импортирован")
        
        print("🎉 Все импорты успешны!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестирования Fereks Feedback Bot\n")
    
    tests = [
        ("Импорты", test_imports),
        ("Конфигурация", test_config),
        ("База данных", test_database)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Тест: {test_name}")
        print('='*50)
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        
        if result:
            passed += 1
            print(f"✅ {test_name}: ПРОЙДЕН")
        else:
            print(f"❌ {test_name}: ПРОВАЛЕН")
    
    print(f"\n{'='*50}")
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print('='*50)
    print(f"Пройдено: {passed}/{total}")
    print(f"Провалено: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\nБот готов к запуску!")
        print("\nДля запуска:")
        print("1. Настройте .env файл с BOT_TOKEN и ADMIN_IDS")
        print("2. Запустите: python main.py")
        return True
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        print("Проверьте ошибки выше и исправьте их.")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка: {e}")
        sys.exit(1)

