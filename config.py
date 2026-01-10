"""
Конфигурация приложения
"""

import os
from pathlib import Path

# Основные настройки
APP_NAME = "Учет рабочего времени и задач"
APP_VERSION = "1.8.1"
DEFAULT_WINDOW_SIZE = "1200x700"

# Пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Настройки БД по умолчанию
DEFAULT_DB_CONFIG = {
    "host": "localhost",
    "database": "work_time_tracking",
    "user": "postgres",
    "password": "12345",
    "port": "5432"
}

# Настройки экспорта
CSV_ENCODING = 'utf-8'
DATE_FORMAT = '%Y%m%d_%H%M%S'