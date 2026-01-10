"""
Тесты для функций обработки данных
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np

# Добавляем путь к проекту для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_processing import extract_emails, clean_csv_data, get_csv_stats

class TestDataProcessing(unittest.TestCase):
    """Тесты для функций обработки данных"""
    
    def test_extract_emails_simple(self):
        """Тест извлечения email-адресов (простой случай)"""
        text = "Контакты: user@example.com и support@company.org"
        emails = extract_emails(text)
        self.assertEqual(len(emails), 2)
        self.assertIn("user@example.com", emails)
        self.assertIn("support@company.org", emails)
    
    def test_extract_emails_multiple(self):
        """Тест извлечения нескольких email-адресов"""
        text = """
        Связь: info@test.ru, sales@company.com.
        Поддержка: help@service.org.
        """
        emails = extract_emails(text)
        self.assertEqual(len(emails), 3)
        self.assertIn("info@test.ru", emails)
        self.assertIn("sales@company.com", emails)
        self.assertIn("help@service.org", emails)
    
    def test_extract_emails_complex(self):
        """Тест извлечения email-адресов со сложными доменами"""
        text = "Email: john.doe123@sub.domain.co.uk или jane_doe@test-mail.com"
        emails = extract_emails(text)
        self.assertEqual(len(emails), 2)
        self.assertIn("john.doe123@sub.domain.co.uk", emails)
        self.assertIn("jane_doe@test-mail.com", emails)
    
    def test_extract_emails_no_emails(self):
        """Тест извлечения email-адресов когда их нет"""
        text = "Текст без email адресов"
        emails = extract_emails(text)
        self.assertEqual(len(emails), 0)
        self.assertEqual(emails, [])
    
    def test_extract_emails_invalid(self):
        """Тест извлечения email-адресов (некорректные адреса)"""
        text = "Некорректные: user@, @domain.com, user@domain"
        emails = extract_emails(text)
        self.assertEqual(len(emails), 0)
        self.assertEqual(emails, [])
    
    def test_clean_csv_data_basic(self):
        """Тест очистки CSV данных (базовый случай)"""
        # Создаем тестовый DataFrame
        data = {
            'Name': ['Иван', 'Петр', None, 'Анна'],
            'Age': [25, 30, 35, None],
            'Email': ['ivan@test.com', 'peter@test.com', None, 'anna@test.com']
        }
        df = pd.DataFrame(data)
        
        # Очищаем данные
        df_cleaned = clean_csv_data(df)
        
        # Проверяем результаты
        self.assertEqual(len(df), 4)  # Исходный размер
        self.assertEqual(len(df_cleaned), 2)  # После очистки осталось 2 строки
        self.assertEqual(list(df_cleaned['Name']), ['Иван', 'Петр'])
        self.assertEqual(list(df_cleaned['Email']), ['ivan@test.com', 'peter@test.com'])
    
    def test_clean_csv_data_empty_strings(self):
        """Тест очистки CSV данных с пустыми строками"""
        data = {
            'A': ['value1', '', 'value3', None],
            'B': [1, 2, None, 4],
            'C': ['', '', '', '']
        }
        df = pd.DataFrame(data)
        
        df_cleaned = clean_csv_data(df)
        
        # Только первая строка полностью заполнена
        self.assertEqual(len(df_cleaned), 1)
        self.assertEqual(df_cleaned.iloc[0]['A'], 'value1')
        self.assertEqual(df_cleaned.iloc[0]['B'], 1)
    
    def test_clean_csv_data_all_valid(self):
        """Тест очистки CSV данных когда все строки валидны"""
        data = {
            'Name': ['А', 'Б', 'В'],
            'Value': [1, 2, 3]
        }
        df = pd.DataFrame(data)
        
        df_cleaned = clean_csv_data(df)
        
        # Все строки должны остаться
        self.assertEqual(len(df), len(df_cleaned))
        pd.testing.assert_frame_equal(df, df_cleaned)
    
    def test_clean_csv_data_empty_dataframe(self):
        """Тест очистки пустого DataFrame"""
        df = pd.DataFrame()
        df_cleaned = clean_csv_data(df)
        
        self.assertEqual(len(df_cleaned), 0)
        self.assertEqual(len(df_cleaned.columns), 0)
    
    def test_get_csv_stats_basic(self):
        """Тест получения статистики CSV (базовый случай)"""
        data = {
            'Name': ['Иван', 'Петр', None, 'Анна'],
            'Age': [25, None, 35, 28],
            'City': ['Москва', 'СПб', None, None]
        }
        df = pd.DataFrame(data)
        
        stats = get_csv_stats(df)
        
        # Проверяем статистику
        self.assertEqual(stats['total_rows'], 4)
        self.assertEqual(stats['total_columns'], 3)
        self.assertEqual(stats['columns'], ['Name', 'Age', 'City'])
        
        # Проверяем подсчет пропущенных значений
        self.assertEqual(stats['missing_values']['Name'], 1)
        self.assertEqual(stats['missing_values']['Age'], 1)
        self.assertEqual(stats['missing_values']['City'], 2)
        self.assertEqual(stats['total_missing'], 4)  # 1 + 1 + 2 = 4
        
        # Проверяем типы данных
        self.assertEqual(stats['dtypes']['Name'], object)
        self.assertEqual(stats['dtypes']['Age'], object)  # Из-за None становится object
    
    def test_get_csv_stats_no_missing(self):
        """Тест получения статистики CSV без пропущенных значений"""
        data = {
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        }
        df = pd.DataFrame(data)
        
        stats = get_csv_stats(df)
        
        self.assertEqual(stats['total_rows'], 3)
        self.assertEqual(stats['total_missing'], 0)
        for count in stats['missing_values'].values():
            self.assertEqual(count, 0)
    
    def test_get_csv_stats_empty(self):
        """Тест получения статистики пустого CSV"""
        df = pd.DataFrame()
        stats = get_csv_stats(df)
        
        self.assertEqual(stats['total_rows'], 0)
        self.assertEqual(stats['total_columns'], 0)
        self.assertEqual(stats['columns'], [])
        self.assertEqual(stats['total_missing'], 0)
        self.assertEqual(stats['missing_values'], {})


if __name__ == '__main__':
    unittest.main()