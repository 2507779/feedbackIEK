from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import FEEDBACK_CATEGORIES, FEEDBACK_TYPES

def get_main_menu():
    """Главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Оставить обратную связь")],
            [KeyboardButton(text="📊 Мои заявки"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard

def get_admin_menu():
    """Админское меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Оставить обратную связь")],
            [KeyboardButton(text="📊 Мои заявки"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="👨‍💼 Админ-панель")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard

def get_feedback_type_keyboard():
    """Клавиатура выбора типа обратной связи"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="😠 Жалоба", callback_data="type_complaint")],
            [InlineKeyboardButton(text="💡 Предложение", callback_data="type_suggestion")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ]
    )
    return keyboard

def get_category_keyboard():
    """Клавиатура выбора категории"""
    keyboard_buttons = []
    
    for key, value in FEEDBACK_CATEGORIES.items():
        keyboard_buttons.append([InlineKeyboardButton(text=value, callback_data=f"cat_{key}")])
    
    keyboard_buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard



def get_confirmation_keyboard():
    """Клавиатура подтверждения отправки"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить", callback_data="confirm_send")],
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="confirm_edit")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ]
    )
    return keyboard

def get_admin_panel_keyboard():
    """Клавиатура админ-панели"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Новые заявки", callback_data="admin_new")],
            [InlineKeyboardButton(text="⏳ В работе", callback_data="admin_progress")],
            [InlineKeyboardButton(text="✅ Закрытые", callback_data="admin_closed")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="🔍 Поиск по категории", callback_data="admin_search")],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="cancel")]
        ]
    )
    return keyboard

def get_feedback_action_keyboard(feedback_id: int):
    """Клавиатура действий с заявкой"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Ответить", callback_data=f"reply_{feedback_id}")],
            [InlineKeyboardButton(text="⏳ В работу", callback_data=f"progress_{feedback_id}")],
            [InlineKeyboardButton(text="✅ Закрыть", callback_data=f"close_{feedback_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
        ]
    )
    return keyboard

def get_back_keyboard():
    """Клавиатура возврата"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
        ]
    )
    return keyboard

def get_pagination_keyboard(page: int, total_pages: int, prefix: str):
    """Клавиатура пагинации"""
    buttons = []
    
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}_page_{page-1}"))
    
    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}_page_{page+1}"))
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            buttons,
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
        ]
    )
    return keyboard

