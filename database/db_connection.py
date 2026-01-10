"""
Модуль для подключения к БД
"""

import psycopg2
from psycopg2 import OperationalError, Error
import config

class DatabaseConnection:
    """Класс для управления подключением к БД"""
    
    def __init__(self, config_dict=None):
        self.connection = None
        self.config = config_dict or config.DEFAULT_DB_CONFIG
        self.is_connected = False
    
    def connect(self):
        """Установить подключение к БД"""
        try:
            self.connection = psycopg2.connect(
                host=self.config["host"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                port=self.config.get("port", "5432")
            )
            self.is_connected = True
            print("Успешное подключение к БД")
            return True
        except OperationalError as e:
            print(f"Ошибка подключения к БД: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Закрыть подключение к БД"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
            print("Подключение к БД закрыто")
    
    def test_connection(self):
        """Тестирование подключения к БД"""
        try:
            if not self.connection or self.connection.closed:
                return self.connect()
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            print(f"Ошибка тестирования подключения: {e}")
            return False
    
    def execute_query(self, query, params=None, fetch=False):
        """Выполнить SQL запрос"""
        if not self.test_connection():
            print("Нет подключения к БД")
            return None
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = None
            cursor.close()
            return result
        except Error as e:
            if self.connection:
                self.connection.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            return None
    
    def get_databases(self):
        """Получить список баз данных на сервере"""
        try:
            query = "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname"
            result = self.execute_query(query, fetch=True)
            return [db[0] for db in result] if result else []
        except Exception as e:
            print(f"Ошибка получения списка БД: {e}")
            return []
    
    def get_tables(self):
        """Получить список таблиц в текущей БД"""
        try:
            query = """
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' ORDER BY table_name
            """
            result = self.execute_query(query, fetch=True)
            return [table[0] for table in result] if result else []
        except Exception as e:
            print(f"Ошибка получения списка таблиц: {e}")
            return []