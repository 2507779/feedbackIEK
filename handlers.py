from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import html

from database import Database
from keyboards import *
from config import FEEDBACK_CATEGORIES, FEEDBACK_TYPES, ADMIN_IDS

router = Router()

# Состояния для FSM
class FeedbackStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_category = State()
    waiting_for_message = State()
    waiting_for_confirmation = State()
    waiting_for_admin_response = State()

# Временное хранилище данных пользователей
user_data = {}

@router.message(Command("start"))
async def cmd_start(message: Message, db: Database):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Добавляем пользователя в базу
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Проверяем, является ли пользователь админом
    is_admin = user.id in ADMIN_IDS
    if is_admin:
        await db.set_admin(user.id, True)
        keyboard = get_admin_menu()
    else:
        keyboard = get_main_menu()
    
    welcome_text = f"""
🏭 <b>Добро пожаловать в систему обратной связи ТД Ферекс!</b>

Привет, {html.escape(user.first_name or user.username or 'пользователь')}!

Этот бот поможет вам:
• Оставить жалобу или предложение
• Отслеживать статус ваших заявок
• Получать ответы от администрации

Выберите действие в меню ниже 👇
"""
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

@router.message(F.text == "📝 Оставить обратную связь")
async def start_feedback(message: Message, state: FSMContext):
    """Начало процесса создания обратной связи"""
    await message.answer(
        "Выберите тип обратной связи:",
        reply_markup=get_feedback_type_keyboard()
    )
    await state.set_state(FeedbackStates.waiting_for_type)

@router.callback_query(F.data.startswith("type_"))
async def process_feedback_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа обратной связи"""
    feedback_type = callback.data.split("_")[1]
    
    await state.update_data(feedback_type=feedback_type)
    
    type_text = "жалобу" if feedback_type == "complaint" else "предложение"
    
    await callback.message.edit_text(
        f"Вы выбрали: <b>{FEEDBACK_TYPES[feedback_type]}</b>\n\n"
        f"Теперь выберите категорию для вашей {type_text}:",
        reply_markup=get_category_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(FeedbackStates.waiting_for_category)

@router.callback_query(F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category_key = callback.data.split("_")[1]
    category_name = FEEDBACK_CATEGORIES[category_key]
    
    await state.update_data(category=category_name)
    
    await callback.message.edit_text(
        f"Категория: <b>{category_name}</b>\n\n"
        "Теперь напишите ваше сообщение. Опишите ситуацию подробно:",
        parse_mode="HTML"
    )
    await state.set_state(FeedbackStates.waiting_for_message)

@router.message(FeedbackStates.waiting_for_message)
async def process_message(message: Message, state: FSMContext):
    """Обработка текста сообщения"""
    if len(message.text) < 10:
        await message.answer("Сообщение слишком короткое. Пожалуйста, опишите ситуацию более подробно (минимум 10 символов).")
        return
    
    await state.update_data(message_text=message.text)
    await state.update_data(is_anonymous=False) # Всегда неанонимно
    
    # Получаем все данные для подтверждения
    data = await state.get_data()
    user = message.from_user
    
    feedback_type_text = FEEDBACK_TYPES[data["feedback_type"]]
    category = data["category"]
    message_text = data["message_text"]
    
    confirmation_text = f"""
<b>Подтверждение отправки</b>

<b>Тип:</b> {feedback_type_text}
<b>Категория:</b> {category}
<b>Отправитель:</b> {user.first_name or user.username}

<b>Сообщение:</b>
{html.escape(message_text)}

Всё верно?
"""
    
    await message.answer(
        confirmation_text,
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(FeedbackStates.waiting_for_confirmation)

@router.callback_query(F.data == "confirm_send")
async def confirm_send(callback: CallbackQuery, state: FSMContext, db: Database):
    """Подтверждение и отправка заявки"""
    data = await state.get_data()
    user = callback.from_user
    
    # Сохраняем заявку в базу данных
    feedback_id = await db.add_feedback(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        category=data['category'],
        feedback_type=data['feedback_type'],
        message=data['message_text'],
        is_anonymous=data['is_anonymous']
    )
    
    # Формируем сообщение для админов
    feedback_type_text = FEEDBACK_TYPES[data['feedback_type']]
    tag = f"[{feedback_type_text}]"
    
    sender_info = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if user.username:
        sender_info += f" (@{user.username})"
    
    admin_message = f"""
🔔 <b>Новая заявка #{feedback_id}</b>

{tag} <b>{data['category']}</b>

<b>От:</b> {sender_info}
<b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

<b>Сообщение:</b>
{html.escape(data['message_text'])}
"""
    
    # Отправляем уведомления админам
    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                admin_message,
                parse_mode="HTML",
                reply_markup=get_feedback_action_keyboard(feedback_id)
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления админу {admin_id}: {e}")
    
    await callback.message.edit_text(
        f"✅ <b>Заявка #{feedback_id} успешно отправлена!</b>\n\n"
        "Ваше сообщение передано администрации. "
        "Вы получите уведомление, когда на него ответят.\n\n"
        "Спасибо за обратную связь!",
        parse_mode="HTML"
    )
    
    await state.clear()

@router.callback_query(F.data == "confirm_edit")
async def confirm_edit(callback: CallbackQuery, state: FSMContext):
    """Возврат к редактированию сообщения"""
    await callback.message.edit_text(
        "Напишите новое сообщение:"
    )
    await state.set_state(FeedbackStates.waiting_for_message)

@router.callback_query(F.data == "cancel")
async def cancel_feedback(callback: CallbackQuery, state: FSMContext):
    """Отмена создания заявки"""
    await callback.message.edit_text("❌ Создание заявки отменено.")
    await state.clear()

@router.message(F.text == "📊 Мои заявки")
async def my_feedback(message: Message, db: Database):
    """Просмотр заявок пользователя"""
    user_id = message.from_user.id
    
    # Получаем заявки пользователя
    feedback_list = await db.get_feedback_list()
    user_feedback = [f for f in feedback_list if f['user_id'] == user_id]
    
    if not user_feedback:
        await message.answer("У вас пока нет заявок.")
        return
    
    text = "<b>📊 Ваши заявки:</b>\n\n"
    
    for feedback in user_feedback[:10]:  # Показываем последние 10
        status_emoji = {
            'new': '🆕',
            'in_progress': '⏳',
            'closed': '✅'
        }
        
        feedback_type = FEEDBACK_TYPES.get(feedback['feedback_type'], feedback['feedback_type'])
        status = status_emoji.get(feedback['status'], '❓')
        
        text += f"{status} <b>#{feedback['id']}</b> - {feedback_type}\n"
        text += f"📂 {feedback['category']}\n"
        text += f"📅 {feedback['created_at'][:16]}\n"
        
        if feedback['admin_response']:
            text += f"💬 <i>Есть ответ</i>\n"
        
        text += "\n"
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "ℹ️ Помощь")
async def help_command(message: Message):
    """Справка по использованию бота"""
    help_text = """
<b>🆘 Справка по использованию бота</b>

<b>Основные функции:</b>
• 📝 Оставить обратную связь - создать новую жалобу или предложение
• 📊 Мои заявки - посмотреть статус ваших заявок
• ℹ️ Помощь - эта справка

<b>Категории обратной связи:</b>
• Цех термопластавтоматов (ТПА)
• Цех литья алюминия
• Монтаж, упаковка, сборка светильников
• Логистика и склад
• HR и кадры
• Общие вопросы

<b>Типы сообщений:</b>
• 😠 Жалоба - сообщить о проблеме
• 💡 Предложение - предложить улучшение

<b>Режимы отправки:</b>
• 👤 Подписать - ваше имя будет видно администрации
• 🕶 Анонимно - ваше имя не будет раскрыто

<b>Статусы заявок:</b>
• 🆕 Новая - заявка получена
• ⏳ В работе - заявка рассматривается
• ✅ Закрыта - заявка обработана

По всем вопросам обращайтесь к администрации.
"""
    
    await message.answer(help_text, parse_mode="HTML")

