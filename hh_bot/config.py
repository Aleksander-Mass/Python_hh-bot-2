""" Константы проекта"""
import os
from dotenv import load_dotenv

# считывает пары ключ-значение из файла .env,и загружает необходимые приложению переменные окружения.
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Параметры поиска вакансий
search_params = {
    'text': None,  # Текст фильтра
    'area': None,  # ИД региона
    'salary': None,  # Заработная плата
    'experience': None,  # Опыт работы.
    'employment': None,  # Тип занятости
    'schedule': None,  # График работы
    'employer_id': None,  # Идентификатор работодателя
    'page': 0,  # Индекс страницы поиска на HH
    'per_page': 100,  # Кол-во вакансий на 1 странице
    'period': 1  # Кол-во дней, пределах которых производится поиск по вакансиям
}

# Команды бота
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку")
)