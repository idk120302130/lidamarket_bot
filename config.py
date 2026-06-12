import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка, что токен был найден
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена. Создайте файл .env!")
