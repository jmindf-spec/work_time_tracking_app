"""
Утилиты для обработки данных
"""

import re
import pandas as pd
import numpy as np

def extract_emails(text):
    """Находит все email-адреса в строке"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)

def clean_csv_data(df):
    """Очищает csv от строк с пустыми значениями"""
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df_cleaned = df.dropna()
    return df_cleaned

def get_csv_stats(df):
    """Получить статистику по DataFrame"""
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict()
    }
    
    # Подсчет пропущенных значений
    df_for_stats = df.replace(r'^\s*$', np.nan, regex=True)
    empty_counts = df_for_stats.isna().sum()
    stats['missing_values'] = empty_counts.to_dict()
    stats['total_missing'] = empty_counts.sum()
    
    return stats