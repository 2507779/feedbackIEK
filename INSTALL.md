# Быстрая установка Fereks Feedback Bot

## Предварительные требования

1. **Создайте Telegram бота**:
   - Найдите [@BotFather](https://t.me/BotFather)
   - Отправьте `/newbot`
   - Сохраните токен

2. **Получите ID администраторов**:
   - Найдите [@userinfobot](https://t.me/userinfobot)
   - Отправьте любое сообщение
   - Скопируйте User ID

## Локальный запуск

```bash
# 1. Клонируйте проект
git clone <repository_url>
cd fereks_feedback_bot

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Настройте переменные окружения
cp .env.example .env
nano .env

# 4. Запустите бота
python main.py
```

## Docker запуск

```bash
# 1. Клонируйте проект
git clone <repository_url>
cd fereks_feedback_bot

# 2. Настройте переменные окружения
cp .env.example .env
nano .env

# 3. Запустите через Docker
docker-compose up -d
```

## Production деплой (systemd)

```bash
# 1. Установите проект
sudo git clone <repository_url> /opt/fereks_feedback_bot
cd /opt/fereks_feedback_bot

# 2. Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Настройте переменные окружения
sudo cp .env.example .env
sudo nano .env

# 4. Создайте директории
sudo mkdir -p data logs
sudo chown -R ubuntu:ubuntu /opt/fereks_feedback_bot

# 5. Установите systemd сервис
sudo cp systemd/fereks-feedback-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/fereks-feedback-bot.service

# 6. Запустите сервис
sudo systemctl daemon-reload
sudo systemctl enable fereks-feedback-bot
sudo systemctl start fereks-feedback-bot
sudo systemctl status fereks-feedback-bot
```

## Настройка .env файла

```env
# Токен бота от BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# ID администраторов (через запятую)
ADMIN_IDS=123456789,987654321,555666777

# Путь к базе данных
DATABASE_PATH=feedback.db
```

## Проверка работы

1. Отправьте `/start` боту
2. Попробуйте создать тестовую заявку
3. Проверьте админ-панель (если вы администратор)

## Полезные команды

```bash
# Просмотр логов (systemd)
sudo journalctl -u fereks-feedback-bot -f

# Просмотр логов (Docker)
docker-compose logs -f

# Перезапуск сервиса
sudo systemctl restart fereks-feedback-bot

# Остановка Docker
docker-compose down
```

Подробная документация в файле [README.md](README.md).

