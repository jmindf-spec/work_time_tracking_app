"""
Тесты для подключения к БД (с использованием моков)
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Добавляем путь к проекту для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock для psycopg2
sys.modules['psycopg2'] = MagicMock()

from database.db_connection import DatabaseConnection
import config

class TestDatabaseConnection(unittest.TestCase):
    """Тесты для класса DatabaseConnection"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_config = {
            "host": "localhost",
            "database": "test_db",
            "user": "test_user",
            "password": "test_pass",
            "port": "5432"
        }
    
    @patch('database.db_connection.psycopg2')
    def test_connect_success(self, mock_psycopg2):
        """Тест успешного подключения к БД"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_psycopg2.connect.return_value = mock_connection
        
        # Создаем и тестируем подключение
        db = DatabaseConnection(self.test_config)
        result = db.connect()
        
        # Проверяем результаты
        self.assertTrue(result)
        self.assertTrue(db.is_connected)
        self.assertEqual(db.connection, mock_connection)
        mock_psycopg2.connect.assert_called_once_with(
            host="localhost",
            database="test_db",
            user="test_user",
            password="test_pass",
            port="5432"
        )
    
    @patch('database.db_connection.psycopg2')
    def test_connect_failure(self, mock_psycopg2):
        """Тест неудачного подключения к БД"""
        # Настраиваем мок на выброс исключения
        mock_psycopg2.connect.side_effect = Exception("Connection failed")
        
        # Создаем и тестируем подключение
        db = DatabaseConnection(self.test_config)
        result = db.connect()
        
        # Проверяем результаты
        self.assertFalse(result)
        self.assertFalse(db.is_connected)
        self.assertIsNone(db.connection)
    
    @patch('database.db_connection.psycopg2')
    def test_disconnect(self, mock_psycopg2):
        """Тест отключения от БД"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_psycopg2.connect.return_value = mock_connection
        
        # Создаем и тестируем подключение/отключение
        db = DatabaseConnection(self.test_config)
        db.connect()
        db.disconnect()
        
        # Проверяем что connection.close() был вызван
        mock_connection.close.assert_called_once()
        self.assertFalse(db.is_connected)
    
    @patch('database.db_connection.psycopg2')
    def test_disconnect_no_connection(self, mock_psycopg2):
        """Тест отключения когда нет подключения"""
        db = DatabaseConnection(self.test_config)
        
        # Не должно быть ошибки при отключении без подключения
        db.disconnect()
        
        # Проверяем что connect не вызывался
        mock_psycopg2.connect.assert_not_called()
    
    @patch('database.db_connection.psycopg2')
    def test_test_connection_success(self, mock_psycopg2):
        """Тест успешной проверки подключения"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_connection
        
        db = DatabaseConnection(self.test_config)
        result = db.test_connection()
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with("SELECT 1")
        mock_cursor.close.assert_called_once()
    
    @patch('database.db_connection.psycopg2')
    def test_test_connection_failure(self, mock_psycopg2):
        """Тест неудачной проверки подключения"""
        # Настраиваем мок на выброс исключения
        mock_psycopg2.connect.side_effect = Exception("Connection failed")
        
        db = DatabaseConnection(self.test_config)
        result = db.test_connection()
        
        self.assertFalse(result)
    
    @patch('database.db_connection.psycopg2')
    def test_execute_query_success(self, mock_psycopg2):
        """Тест успешного выполнения запроса"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('result1',), ('result2',)]
        mock_psycopg2.connect.return_value = mock_connection
        
        db = DatabaseConnection(self.test_config)
        db.connect()
        
        # Тестируем запрос с fetch
        result = db.execute_query("SELECT * FROM test", fetch=True)
        
        self.assertEqual(result, [('result1',), ('result2',)])
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", ())
        mock_cursor.fetchall.assert_called_once()
        mock_connection.commit.assert_not_called()  # При fetch commit не вызывается
    
    @patch('database.db_connection.psycopg2')
    def test_execute_query_no_fetch(self, mock_psycopg2):
        """Тест выполнения запроса без fetch"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_connection
        
        db = DatabaseConnection(self.test_config)
        db.connect()
        
        # Тестируем запрос без fetch
        result = db.execute_query("INSERT INTO test VALUES (1)", fetch=False)
        
        self.assertIsNone(result)
        mock_cursor.execute.assert_called_once_with("INSERT INTO test VALUES (1)", ())
        mock_cursor.fetchall.assert_not_called()
        mock_connection.commit.assert_called_once()
    
    @patch('database.db_connection.psycopg2')
    def test_execute_query_with_params(self, mock_psycopg2):
        """Тест выполнения запроса с параметрами"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_connection
        
        db = DatabaseConnection(self.test_config)
        db.connect()
        
        # Тестируем запрос с параметрами
        params = ('value1', 123)
        db.execute_query("INSERT INTO test (a, b) VALUES (%s, %s)", params)
        
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO test (a, b) VALUES (%s, %s)",
            ('value1', 123)
        )
    
    @patch('database.db_connection.psycopg2')
    def test_execute_query_error(self, mock_psycopg2):
        """Тест выполнения запроса с ошибкой"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_psycopg2.connect.return_value = mock_connection
        
        db = DatabaseConnection(self.test_config)
        db.connect()
        
        # Тестируем запрос с ошибкой
        result = db.execute_query("INVALID SQL")
        
        self.assertIsNone(result)
        mock_connection.rollback.assert_called_once()
    
    @patch('database.db_connection.psycopg2')
    def test_get_databases(self, mock_psycopg2):
        """Тест получения списка баз данных"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('database1',),
            ('database2',),
            ('database3',)
        ]
        mock_psycopg2.connect.return_value = mock_connection
        
        db = DatabaseConnection(self.test_config)
        db.connect()
        
        databases = db.get_databases()
        
        self.assertEqual(databases, ['database1', 'database2', 'database3'])
        mock_cursor.execute.assert_called_once_with(
            "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname"
        )
    
    @patch('database.db_connection.psycopg2')
    def test_get_tables(self, mock_psycopg2):
        """Тест получения списка таблиц"""
        # Настраиваем мок
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('table1',),
            ('table2',),
            ('table3',)
        ]
        mock_psycopg2.connect.return_value = mock_connection
        
        db = DatabaseConnection(self.test_config)
        db.connect()
        
        tables = db.get_tables()
        
        self.assertEqual(tables, ['table1', 'table2', 'table3'])
        expected_query = """
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' ORDER BY table_name
            """
        mock_cursor.execute.assert_called_once_with(expected_query.strip())


if __name__ == '__main__':
    unittest.main()