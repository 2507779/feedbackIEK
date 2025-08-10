from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import html
import math

from database import Database
from keyboards import *
from config import FEEDBACK_CATEGORIES, FEEDBACK_TYPES, FEEDBACK_STATUSES, ADMIN_IDS

router = Router()

# Состояния для админки
class AdminStates(StatesGroup):
    waiting_for_response = State()

@router.message(F.text == "👨‍💼 Админ-панель")
async def admin_panel(message: Message, db: Database):
    """Главная админ-панель"""
    user_id = message.from_user.id
    
    if user_id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    # Получаем статистику
    stats = await db.get_stats()
    
    stats_text = f"""
<b>👨‍💼 Админ-панель</b>

<b>📊 Статистика заявок:</b>
• Всего: {stats['total']}
• Новые: {stats['new']}
• В работе: {stats['in_progress']}
• Закрытые: {stats['closed']}

Выберите действие:
"""
    
    await message.answer(
        stats_text,
        reply_markup=get_admin_panel_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery, db: Database):
    """Возврат в админ-панель"""
    user_id = callback.from_user.id
    
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    # Получаем статистику
    stats = await db.get_stats()
    
    stats_text = f"""
<b>👨‍💼 Админ-панель</b>

<b>📊 Статистика заявок:</b>
• Всего: {stats['total']}
• Новые: {stats['new']}
• В работе: {stats['in_progress']}
• Закрытые: {stats['closed']}

Выберите действие:
"""
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_admin_panel_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("admin_"))
async def admin_actions(callback: CallbackQuery, db: Database):
    """Обработка админских действий"""
    user_id = callback.from_user.id
    
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    action = callback.data.split("_")[1]
    
    if action == "new":
        await show_feedback_list(callback, db, "new", "🆕 Новые заявки")
    elif action == "progress":
        await show_feedback_list(callback, db, "in_progress", "⏳ Заявки в работе")
    elif action == "closed":
        await show_feedback_list(callback, db, "closed", "✅ Закрытые заявки")
    elif action == "stats":
        await show_detailed_stats(callback, db)
    elif action == "search":
        await show_category_search(callback, db)

async def show_feedback_list(callback: CallbackQuery, db: Database, status: str, title: str, page: int = 1):
    """Показать список заявок"""
    per_page = 5
    offset = (page - 1) * per_page
    
    # Получаем заявки
    all_feedback = await db.get_feedback_list(status=status, limit=100)
    total_count = len(all_feedback)
    feedback_list = all_feedback[offset:offset + per_page]
    
    if not feedback_list:
        await callback.message.edit_text(
            f"{title}\n\nЗаявок не найдено.",
            reply_markup=get_back_keyboard()
        )
        return
    
    text = f"<b>{title}</b>\n\n"
    
    for feedback in feedback_list:
        feedback_type = FEEDBACK_TYPES.get(feedback['feedback_type'], feedback['feedback_type'])
        
        if feedback['is_anonymous']:
            sender = "Анонимно"
        else:
            sender = f"{feedback['first_name'] or ''} {feedback['last_name'] or ''}".strip()
            if feedback['username']:
                sender += f" (@{feedback['username']})"
        
        text += f"<b>#{feedback['id']}</b> - {feedback_type}\n"
        text += f"📂 {feedback['category']}\n"
        text += f"👤 {sender}\n"
        text += f"📅 {feedback['created_at'][:16]}\n"
        text += f"💬 {feedback['message'][:100]}{'...' if len(feedback['message']) > 100 else ''}\n"
        text += f"<a href='tg://user?id={callback.from_user.id}'>Подробнее #{feedback['id']}</a>\n\n"
    
    # Пагинация
    total_pages = math.ceil(total_count / per_page)
    if total_pages > 1:
        keyboard = get_pagination_keyboard(page, total_pages, f"admin_{status}")
    else:
        keyboard = get_back_keyboard()
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("admin_") & F.data.contains("_page_"))
async def admin_pagination(callback: CallbackQuery, db: Database):
    """Обработка пагинации в админке"""
    user_id = callback.from_user.id
    
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    parts = callback.data.split("_")
    status = parts[1]
    page = int(parts[3])
    
    title_map = {
        "new": "🆕 Новые заявки",
        "progress": "⏳ Заявки в работе", 
        "closed": "✅ Закрытые заявки"
    }
    
    await show_feedback_list(callback, db, status, title_map[status], page)

async def show_detailed_stats(callback: CallbackQuery, db: Database):
    """Показать детальную статистику"""
    stats = await db.get_stats()
    
    # Получаем статистику по категориям
    all_feedback = await db.get_feedback_list(limit=1000)
    
    category_stats = {}
    type_stats = {"complaint": 0, "suggestion": 0}
    
    for feedback in all_feedback:
        # Статистика по категориям
        category = feedback['category']
        if category not in category_stats:
            category_stats[category] = {"total": 0, "new": 0, "in_progress": 0, "closed": 0}
        
        category_stats[category]["total"] += 1
        category_stats[category][feedback['status']] += 1
        
        # Статистика по типам
        if feedback['feedback_type'] in type_stats:
            type_stats[feedback['feedback_type']] += 1
    
    text = f"""
<b>📊 Детальная статистика</b>

<b>Общая статистика:</b>
• Всего заявок: {stats['total']}
• Новые: {stats['new']}
• В работе: {stats['in_progress']}
• Закрытые: {stats['closed']}

<b>По типам:</b>
• Жалобы: {type_stats['complaint']}
• Предложения: {type_stats['suggestion']}

<b>По категориям:</b>
"""
    
    for category, cat_stats in category_stats.items():
        text += f"\n<b>{category}:</b>\n"
        text += f"  • Всего: {cat_stats['total']}\n"
        text += f"  • Новые: {cat_stats['new']}\n"
        text += f"  • В работе: {cat_stats['in_progress']}\n"
        text += f"  • Закрытые: {cat_stats['closed']}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )

async def show_category_search(callback: CallbackQuery, db: Database):
    """Показать поиск по категориям"""
    text = "<b>🔍 Поиск по категориям</b>\n\nВыберите категорию:"
    
    keyboard_buttons = []
    for key, value in FEEDBACK_CATEGORIES.items():
        keyboard_buttons.append([InlineKeyboardButton(text=value, callback_data=f"search_cat_{key}")])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("search_cat_"))
async def search_by_category(callback: CallbackQuery, db: Database):
    """Поиск заявок по категории"""
    user_id = callback.from_user.id
    
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    category_key = callback.data.split("_")[2]
    category_name = FEEDBACK_CATEGORIES[category_key]
    
    await show_feedback_list(callback, db, None, f"🔍 Поиск: {category_name}", category=category_name)

@router.callback_query(F.data.startswith("reply_"))
async def reply_to_feedback(callback: CallbackQuery, state: FSMContext, db: Database):
    """Ответ на заявку"""
    user_id = callback.from_user.id
    
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    feedback_id = int(callback.data.split("_")[1])
    
    # Получаем заявку
    feedback = await db.get_feedback_by_id(feedback_id)
    if not feedback:
        await callback.answer("❌ Заявка не найдена.")
        return
    
    await state.update_data(feedback_id=feedback_id)
    
    await callback.message.edit_text(
        f"<b>Ответ на заявку #{feedback_id}</b>\n\n"
        "Напишите ваш ответ:",
        parse_mode="HTML"
    )
    
    await state.set_state(AdminStates.waiting_for_response)

@router.message(AdminStates.waiting_for_response)
async def process_admin_response(message: Message, state: FSMContext, db: Database):
    """Обработка ответа админа"""
    data = await state.get_data()
    feedback_id = data['feedback_id']
    admin_response = message.text
    
    # Получаем заявку
    feedback = await db.get_feedback_by_id(feedback_id)
    if not feedback:
        await message.answer("❌ Заявка не найдена.")
        await state.clear()
        return
    
    # Обновляем заявку
    await db.update_feedback_status(
        feedback_id=feedback_id,
        status="closed",
        admin_id=message.from_user.id,
        admin_response=admin_response
    )
    
    # Отправляем ответ пользователю (если не анонимно)
    if not feedback['is_anonymous'] and feedback['user_id']:
        try:
            user_message = f"""
✅ <b>Получен ответ на вашу заявку #{feedback_id}</b>

<b>Ваше сообщение:</b>
{html.escape(feedback['message'][:200])}{'...' if len(feedback['message']) > 200 else ''}

<b>Ответ администрации:</b>
{html.escape(admin_response)}

<b>Дата ответа:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
            
            await message.bot.send_message(
                feedback['user_id'],
                user_message,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка отправки ответа пользователю {feedback['user_id']}: {e}")
    
    await message.answer(
        f"✅ Ответ на заявку #{feedback_id} отправлен и заявка закрыта.",
        reply_markup=get_admin_menu()
    )
    
    await state.clear()

@router.callback_query(F.data.startswith("progress_"))
async def set_in_progress(callback: CallbackQuery, db: Database):
    """Перевести заявку в статус 'в работе'"""
    user_id = callback.from_user.id
    
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    feedback_id = int(callback.data.split("_")[1])
    
    await db.update_feedback_status(
        feedback_id=feedback_id,
        status="in_progress",
        admin_id=user_id
    )
    
    await callback.answer("✅ Заявка переведена в работу.")
    
    # Обновляем сообщение
    feedback = await db.get_feedback_by_id(feedback_id)
    if feedback:
        await callback.message.edit_reply_markup(
            reply_markup=get_feedback_action_keyboard(feedback_id)
        )

@router.callback_query(F.data.startswith("close_"))
async def close_feedback(callback: CallbackQuery, db: Database):
    """Закрыть заявку без ответа"""
    user_id = callback.from_user.id
    
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    feedback_id = int(callback.data.split("_")[1])
    
    await db.update_feedback_status(
        feedback_id=feedback_id,
        status="closed",
        admin_id=user_id
    )
    
    await callback.answer("✅ Заявка закрыта.")
    
    # Обновляем сообщение
    feedback = await db.get_feedback_by_id(feedback_id)
    if feedback:
        await callback.message.edit_reply_markup(
            reply_markup=get_feedback_action_keyboard(feedback_id)
        )

