"""
Утилиты для работы с файлами
"""

import pandas as pd
import os
from datetime import datetime
import config

def export_to_csv(data, filename_prefix, index=False):
    """Экспорт данных в CSV файл"""
    filename = f"{filename_prefix}_{datetime.now().strftime(config.DATE_FORMAT)}.csv"
    data.to_csv(filename, index=index, encoding=config.CSV_ENCODING)
    return filename

def save_cleaned_csv(df, original_path):
    """Сохранить очищенный CSV файл"""
    file_dir = os.path.dirname(original_path)
    file_name = os.path.basename(original_path)
    name_without_ext = os.path.splitext(file_name)[0]
    cleaned_file_name = f"{name_without_ext}_cleaned.csv"
    cleaned_file_path = os.path.join(file_dir, cleaned_file_name)
    
    df.to_csv(cleaned_file_path, index=False, encoding=config.CSV_ENCODING)
    return cleaned_file_path

def get_file_info(filepath):
    """Получить информацию о файле"""
    if not os.path.exists(filepath):
        return None
    
    stats = os.stat(filepath)
    return {
        'path': filepath,
        'name': os.path.basename(filepath),
        'size': stats.st_size,
        'created': datetime.fromtimestamp(stats.st_ctime),
        'modified': datetime.fromtimestamp(stats.st_mtime)
    }