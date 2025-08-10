import aiosqlite
import asyncio
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица заявок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    feedback_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_anonymous BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'new',
                    admin_response TEXT,
                    admin_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица категорий
            await db.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            await db.commit()
            
            # Добавляем базовые категории
            await self.init_categories()

    async def init_categories(self):
        """Инициализация базовых категорий"""
        categories = [
            ("Цех термопластавтоматов (ТПА)", "Вопросы по работе цеха ТПА"),
            ("Цех литья алюминия", "Вопросы по работе цеха литья алюминия"),
            ("Монтаж, упаковка, сборка светильников", "Вопросы по монтажу и сборке"),
            ("Логистика и склад", "Вопросы по логистике и складским операциям"),
            ("HR и кадры", "Вопросы по кадровой политике"),
            ("Общие вопросы", "Общие вопросы по работе предприятия")
        ]
        
        async with aiosqlite.connect(self.db_path) as db:
            for name, description in categories:
                await db.execute(
                    "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                    (name, description)
                )
            await db.commit()

    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None):
        """Добавление пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name) 
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, last_name))
            await db.commit()

    async def set_admin(self, user_id: int, is_admin: bool = True):
        """Установка админских прав"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_admin = ? WHERE user_id = ?",
                (is_admin, user_id)
            )
            await db.commit()

    async def is_admin(self, user_id: int) -> bool:
        """Проверка админских прав"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT is_admin FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else False

    async def add_feedback(self, user_id: int, username: str, first_name: str, 
                          last_name: str, category: str, feedback_type: str, 
                          message: str, is_anonymous: bool = False, 
                          subcategory: str = None) -> int:
        """Добавление заявки"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO feedback 
                (user_id, username, first_name, last_name, category, subcategory,
                 feedback_type, message, is_anonymous) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, category, 
                  subcategory, feedback_type, message, is_anonymous))
            await db.commit()
            return cursor.lastrowid

    async def get_feedback_list(self, status: str = None, category: str = None, 
                               limit: int = 50) -> List[Dict]:
        """Получение списка заявок"""
        query = "SELECT * FROM feedback WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_feedback_by_id(self, feedback_id: int) -> Optional[Dict]:
        """Получение заявки по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM feedback WHERE id = ?",
                (feedback_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_feedback_status(self, feedback_id: int, status: str, 
                                   admin_id: int = None, admin_response: str = None):
        """Обновление статуса заявки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE feedback 
                SET status = ?, admin_id = ?, admin_response = ?, 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (status, admin_id, admin_response, feedback_id))
            await db.commit()

    async def get_categories(self) -> List[Dict]:
        """Получение списка категорий"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM categories WHERE is_active = TRUE ORDER BY name"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_stats(self) -> Dict:
        """Получение статистики"""
        async with aiosqlite.connect(self.db_path) as db:
            # Общее количество заявок
            cursor = await db.execute("SELECT COUNT(*) FROM feedback")
            total = (await cursor.fetchone())[0]
            
            # Новые заявки
            cursor = await db.execute("SELECT COUNT(*) FROM feedback WHERE status = 'new'")
            new = (await cursor.fetchone())[0]
            
            # Заявки в работе
            cursor = await db.execute("SELECT COUNT(*) FROM feedback WHERE status = 'in_progress'")
            in_progress = (await cursor.fetchone())[0]
            
            # Закрытые заявки
            cursor = await db.execute("SELECT COUNT(*) FROM feedback WHERE status = 'closed'")
            closed = (await cursor.fetchone())[0]
            
            return {
                'total': total,
                'new': new,
                'in_progress': in_progress,
                'closed': closed
            }

