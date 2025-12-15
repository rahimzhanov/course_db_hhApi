# config.py
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройки подключения к БД
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "hh_vacancies"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgre"),
    "port": os.getenv("DB_PORT", 5432)
}
# ID компаний с hh.ru (пример - можно изменить)
COMPANIES = {
    "Яндекс": 1740,
    "VK": 15478,
    "Сбер": 3529,
    "Тинькофф": 78638,
    "OZON": 2180,
    "Альфа-Банк": 80,
    "МТС": 3776,
    "Ростелеком": 2748,
    "Газпром нефть": 39305,
    "Лукойл": 907345
}

# Настройки базы данных из переменных окружения
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "hh_vacancies"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgre"),
    "port": os.getenv("DB_PORT", 5432)
}

# Настройки API HH
API_BASE_URL = "https://api.hh.ru"
USER_AGENT = "HH-Data-Collection-App/1.0 amanrahim2@gmail.com"  # Замените на свой email

# Параметры для сбора данных
MAX_VACANCIES_PER_COMPANY = 2000  # Ограничение на сбор вакансий
REQUEST_DELAY = 0.1  # Задержка между запросами в секундах