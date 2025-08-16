# Премиум-бот обратной связи ТД Ферекс

Telegram-бот для сбора обратной связи от сотрудников ТД Ферекс с полным функционалом для производственных цехов.

## Возможности

### Для сотрудников:
- 📝 Отправка жалоб и предложений по категориям
- ✅ Промежуточное меню подтверждения
- 📊 Просмотр статуса своих заявок
- 💬 Получение ответов от администрации

### Для администраторов:
- 👨‍💼 Полноценная админ-панель в боте
- 📋 Просмотр заявок по статусам (новые, в работе, закрытые)
- 🔍 Фильтрация по категориям
- 📊 Детальная статистика
- 💬 Ответы на заявки с уведомлениями
- 🔔 Автоматические уведомления о новых заявках

### Технические особенности:
- 🗄️ Логирование всех заявок в SQLite
- 🏷️ Служебные теги [ЖАЛОБА], [ПРЕДЛОЖЕНИЕ]
- 🎨 HTML-форматирование сообщений
- 🐳 Поддержка Docker для деплоя
- ⚙️ Systemd сервис для production

## Категории обратной связи

1. **Цех термопластавтоматов (ТПА)** - вопросы по работе цеха ТПА
2. **Цех литья алюминия** - вопросы по работе цеха литья алюминия  
3. **Монтаж, упаковка, сборка светильников** - вопросы по монтажу и сборке
4. **Логистика и склад** - вопросы по логистике и складским операциям
5. **HR и кадры** - вопросы по кадровой политике
6. **Общие вопросы** - общие вопросы по работе предприятия

## Структура проекта

```
fereks_feedback_bot/
├── main.py                    # Главный файл запуска бота
├── config.py                  # Конфигурация и настройки
├── database.py                # Модуль работы с базой данных
├── handlers.py                # Основные обработчики сообщений
├── admin_handlers.py          # Обработчики админ-панели
├── keyboards.py               # Клавиатуры и кнопки
├── requirements.txt           # Зависимости Python
├── .env.example              # Пример файла конфигурации
├── Dockerfile                # Docker образ
├── docker-compose.yml        # Docker Compose конфигурация
├── systemd/                  # Systemd сервис файлы
│   └── fereks-feedback-bot.service
├── data/                     # Директория для базы данных
├── logs/                     # Директория для логов
└── README.md                 # Документация
```

## Требования

- Python 3.11+
- Telegram Bot Token
- Docker (опционально)

## Зависимости

- `aiogram==3.3.0` - Telegram Bot API
- `aiosqlite==0.19.0` - Асинхронная работа с SQLite
- `python-dotenv==1.0.0` - Загрузка переменных окружения



## Установка и настройка

### 1. Создание Telegram бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 2. Получение ID администраторов

1. Найдите [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправьте ему любое сообщение
3. Скопируйте ваш User ID
4. Повторите для всех администраторов

### 3. Клонирование проекта

```bash
git clone <repository_url>
cd fereks_feedback_bot
```

### 4. Настройка переменных окружения

Скопируйте файл примера и отредактируйте его:

```bash
cp .env.example .env
nano .env
```

Заполните следующие переменные:

```env
# Telegram Bot Token (получен от BotFather)
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Admin User IDs (через запятую)
ADMIN_IDS=123456789,987654321,555666777

# Database path (по умолчанию)
DATABASE_PATH=feedback.db
```

## Запуск локально

### Вариант 1: Прямой запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите бота:
```bash
python main.py
```

### Вариант 2: Виртуальное окружение

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите бота:
```bash
python main.py
```

### Вариант 3: Docker

1. Создайте файл `.env` с настройками
2. Запустите через Docker Compose:

```bash
docker-compose up -d
```

Для просмотра логов:
```bash
docker-compose logs -f
```

Для остановки:
```bash
docker-compose down
```


## Деплой в production (systemd)

### 1. Подготовка сервера

Создайте пользователя для бота (опционально):
```bash
sudo useradd -m -s /bin/bash fereks-bot
sudo usermod -aG sudo fereks-bot
```

### 2. Установка проекта

```bash
# Клонируйте проект в /opt
sudo git clone <repository_url> /opt/fereks_feedback_bot
sudo chown -R ubuntu:ubuntu /opt/fereks_feedback_bot

# Перейдите в директорию
cd /opt/fereks_feedback_bot

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

```bash
# Создайте файл конфигурации
sudo cp .env.example /opt/fereks_feedback_bot/.env
sudo nano /opt/fereks_feedback_bot/.env
```

Заполните переменные:
```env
BOT_TOKEN=your_real_bot_token_here
ADMIN_IDS=123456789,987654321
DATABASE_PATH=/opt/fereks_feedback_bot/data/feedback.db
```

### 4. Создание директорий

```bash
sudo mkdir -p /opt/fereks_feedback_bot/data
sudo mkdir -p /opt/fereks_feedback_bot/logs
sudo chown -R ubuntu:ubuntu /opt/fereks_feedback_bot
```

### 5. Установка systemd сервиса

```bash
# Скопируйте файл сервиса
sudo cp systemd/fereks-feedback-bot.service /etc/systemd/system/

# Отредактируйте пути и переменные в файле сервиса
sudo nano /etc/systemd/system/fereks-feedback-bot.service
```

Убедитесь, что в файле сервиса указаны правильные пути и переменные:
```ini
[Unit]
Description=Fereks Feedback Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/fereks_feedback_bot
Environment=PATH=/opt/fereks_feedback_bot/venv/bin
ExecStart=/opt/fereks_feedback_bot/venv/bin/python main.py
Restart=always
RestartSec=10

# Переменные окружения
EnvironmentFile=/opt/fereks_feedback_bot/.env

# Логирование
StandardOutput=journal
StandardError=journal
SyslogIdentifier=fereks-feedback-bot

[Install]
WantedBy=multi-user.target
```

### 6. Запуск сервиса

```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable fereks-feedback-bot

# Запустите сервис
sudo systemctl start fereks-feedback-bot

# Проверьте статус
sudo systemctl status fereks-feedback-bot
```

### 7. Управление сервисом

```bash
# Просмотр логов
sudo journalctl -u fereks-feedback-bot -f

# Перезапуск
sudo systemctl restart fereks-feedback-bot

# Остановка
sudo systemctl stop fereks-feedback-bot

# Отключение автозапуска
sudo systemctl disable fereks-feedback-bot
```

### 8. Обновление бота

```bash
# Остановите сервис
sudo systemctl stop fereks-feedback-bot

# Обновите код
cd /opt/fereks_feedback_bot
sudo git pull

# Обновите зависимости (если нужно)
source venv/bin/activate
pip install -r requirements.txt

# Запустите сервис
sudo systemctl start fereks-feedback-bot
```


## Использование

### Для сотрудников

1. **Начало работы**: Отправьте `/start` боту
2. **Создание заявки**: Нажмите "📝 Оставить обратную связь"
3. **Выбор типа**: Выберите "Жалоба" или "Предложение"
4. **Выбор категории**: Выберите подходящий цех/отдел
5. **Написание сообщения**: Опишите ситуацию подробно

7. **Подтверждение**: Проверьте данные и отправьте

### Для администраторов

1. **Доступ к админ-панели**: Нажмите "👨‍💼 Админ-панель"
2. **Просмотр заявок**: 
   - "📋 Новые заявки" - непрочитанные заявки
   - "⏳ В работе" - заявки в процессе обработки
   - "✅ Закрытые" - обработанные заявки
3. **Работа с заявкой**:
   - "📝 Ответить" - отправить ответ пользователю
   - "⏳ В работу" - перевести в статус "в работе"
   - "✅ Закрыть" - закрыть без ответа
4. **Статистика**: "📊 Статистика" - общая статистика по заявкам
5. **Поиск**: "🔍 Поиск по категории" - фильтрация по цехам

## База данных

Бот использует SQLite базу данных со следующими таблицами:

### users
- `id` - первичный ключ
- `user_id` - Telegram ID пользователя
- `username` - имя пользователя в Telegram
- `first_name` - имя
- `last_name` - фамилия
- `is_admin` - флаг администратора
- `created_at` - дата регистрации

### feedback
- `id` - первичный ключ заявки
- `user_id` - ID пользователя
- `username` - имя пользователя
- `first_name` - имя
- `last_name` - фамилия
- `category` - категория (цех/отдел)
- `subcategory` - подкатегория (резерв)
- `feedback_type` - тип (complaint/suggestion)
- `message` - текст сообщения
- `is_anonymous` - анонимная заявка
- `status` - статус (new/in_progress/closed)
- `admin_response` - ответ администратора
- `admin_id` - ID администратора, обработавшего заявку
- `created_at` - дата создания
- `updated_at` - дата обновления

### categories
- `id` - первичный ключ
- `name` - название категории
- `description` - описание
- `is_active` - активная категория

## Устранение неполадок

### Бот не отвечает

1. Проверьте токен бота:
```bash
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

2. Проверьте логи:
```bash
# Для systemd
sudo journalctl -u fereks-feedback-bot -f

# Для Docker
docker-compose logs -f
```

3. Проверьте переменные окружения:
```bash
cat .env
```

### Ошибки базы данных

1. Проверьте права доступа к файлу базы данных:
```bash
ls -la data/feedback.db
```

2. Пересоздайте базу данных:
```bash
rm data/feedback.db
python main.py  # База создастся автоматически
```

### Админы не получают уведомления

1. Проверьте правильность ID администраторов в `.env`
2. Убедитесь, что администраторы запустили бота (`/start`)
3. Проверьте логи на ошибки отправки сообщений

### Docker проблемы

1. Проверьте статус контейнера:
```bash
docker-compose ps
```

2. Просмотрите логи:
```bash
docker-compose logs fereks-feedback-bot
```

3. Пересоберите образ:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Безопасность

1. **Токен бота**: Никогда не публикуйте токен бота в открытом доступе
2. **Переменные окружения**: Используйте `.env` файл для конфиденциальных данных
3. **Права доступа**: Ограничьте доступ к файлам проекта
4. **Резервное копирование**: Регулярно создавайте резервные копии базы данных

## Лицензия

Проект разработан для внутреннего использования ТД Ферекс.

## Поддержка

По вопросам работы бота обращайтесь к администрации ТД Ферекс.

