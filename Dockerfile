# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директорию для базы данных
RUN mkdir -p /app/data

# Устанавливаем переменную окружения для базы данных
ENV DATABASE_PATH=/app/data/feedback.db

# Открываем порт (если потребуется веб-интерфейс)
EXPOSE 8000

# Команда запуска
CMD ["python", "main.py"]

