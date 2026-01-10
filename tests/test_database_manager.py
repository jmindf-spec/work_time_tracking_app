"""
Тесты для DatabaseManager (с использованием моков)
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch, call

# Добавляем путь к проекту для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import DatabaseManager
from models.employee import Employee
from models.task import Task
from models.project import Project

class TestDatabaseManager(unittest.TestCase):
    """Тесты для класса DatabaseManager"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.mock_db = MagicMock()
        self.db_manager = DatabaseManager(self.mock_db)
        
        # Тестовые данные для сотрудников
        self.test_employee_data = [
            (1, 'Иван Иванов', 'Разработчик', 100000),
            (2, 'Петр Петров', 'Менеджер', 80000)
        ]
        
        # Тестовые данные для задач
        self.test_task_data = [
            (1, 'Задача 1', 'Описание 1', 'В процессе', 40, 1, 1, 'Иван Иванов', 'Проект 1'),
            (2, 'Задача 2', 'Описание 2', 'Завершено', 20, 2, 1, 'Петр Петров', 'Проект 1')
        ]
        
        # Тестовые данные для проектов
        self.test_project_data = [
            (1, 'Проект 1'),
            (2, 'Проект 2')
        ]
    
    def test_get_all_employees(self):
        """Тест получения всех сотрудников"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = self.test_employee_data
        
        # Вызываем метод
        employees = self.db_manager.get_all_employees()
        
        # Проверяем результаты
        self.assertEqual(len(employees), 2)
        
        # Проверяем первого сотрудника
        self.assertEqual(employees[0].id, 1)
        self.assertEqual(employees[0].name, 'Иван Иванов')
        self.assertEqual(employees[0].position, 'Разработчик')
        self.assertEqual(employees[0].salary, 100000)
        
        # Проверяем второго сотрудника
        self.assertEqual(employees[1].id, 2)
        self.assertEqual(employees[1].name, 'Петр Петров')
        self.assertEqual(employees[1].position, 'Менеджер')
        self.assertEqual(employees[1].salary, 80000)
        
        # Проверяем вызовы
        self.mock_db.execute_query.assert_called_once_with(
            "SELECT id, name, position, salary FROM employees ORDER BY id",
            fetch=True
        )
    
    def test_get_employee_by_id(self):
        """Тест получения сотрудника по ID"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = [(1, 'Иван Иванов', 'Разработчик', 100000)]
        
        # Вызываем метод
        employee = self.db_manager.get_employee_by_id(1)
        
        # Проверяем результаты
        self.assertIsNotNone(employee)
        self.assertEqual(employee.id, 1)
        self.assertEqual(employee.name, 'Иван Иванов')
        self.assertEqual(employee.position, 'Разработчик')
        self.assertEqual(employee.salary, 100000)
        
        # Проверяем вызов
        self.mock_db.execute_query.assert_called_once_with(
            "SELECT id, name, position, salary FROM employees WHERE id = %s",
            (1,),
            fetch=True
        )
    
    def test_get_employee_by_id_not_found(self):
        """Тест получения несуществующего сотрудника"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = []
        
        # Вызываем метод
        employee = self.db_manager.get_employee_by_id(999)
        
        # Проверяем результаты
        self.assertIsNone(employee)
    
    def test_get_employee_hours_worked(self):
        """Тест получения отработанных часов сотрудника"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = [(60.5,)]
        
        # Вызываем метод
        hours = self.db_manager.get_employee_hours_worked(1)
        
        # Проверяем результаты
        self.assertEqual(hours, 60.5)
        
        # Проверяем вызов
        expected_query = """
            SELECT COALESCE(SUM(hours_required), 0) 
            FROM tasks 
            WHERE employee_id = %s AND status = 'Завершено'
        """
        self.mock_db.execute_query.assert_called_once_with(
            expected_query.strip(),
            (1,),
            fetch=True
        )
    
    def test_add_employee(self):
        """Тест добавления сотрудника"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = [(5,)]  # Возвращаемый ID
        
        # Создаем сотрудника
        employee = Employee('Новый Сотрудник', 'Тестировщик', 70000)
        
        # Вызываем метод
        result = self.db_manager.add_employee(employee)
        
        # Проверяем результаты
        self.assertEqual(result, 5)
        self.assertEqual(employee.id, 5)
        
        # Проверяем вызов
        self.mock_db.execute_query.assert_called_once_with(
            """
            INSERT INTO employees (name, position, salary)
            VALUES (%s, %s, %s) RETURNING id
        """.strip(),
            ('Новый Сотрудник', 'Тестировщик', 70000),
            fetch=True
        )
    
    def test_update_employee(self):
        """Тест обновления сотрудника"""
        # Создаем сотрудника
        employee = Employee('Иван Иванов', 'Старший разработчик', 120000, emp_id=1)
        
        # Вызываем метод
        self.db_manager.update_employee(employee)
        
        # Проверяем вызов
        self.mock_db.execute_query.assert_called_once_with(
            """
            UPDATE employees 
            SET name = %s, position = %s, salary = %s
            WHERE id = %s
        """.strip(),
            ('Иван Иванов', 'Старший разработчик', 120000, 1),
            fetch=False
        )
    
    def test_delete_employee(self):
        """Тест удаления сотрудника"""
        # Вызываем метод
        self.db_manager.delete_employee(1)
        
        # Проверяем вызов
        self.mock_db.execute_query.assert_called_once_with(
            "DELETE FROM employees WHERE id = %s",
            (1,),
            fetch=False
        )
    
    def test_get_all_tasks(self):
        """Тест получения всех задач"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = self.test_task_data
        
        # Вызываем метод
        tasks = self.db_manager.get_all_tasks()
        
        # Проверяем результаты
        self.assertEqual(len(tasks), 2)
        
        # Проверяем первую задачу
        self.assertEqual(tasks[0].id, 1)
        self.assertEqual(tasks[0].title, 'Задача 1')
        self.assertEqual(tasks[0].description, 'Описание 1')
        self.assertEqual(tasks[0].status, 'В процессе')
        self.assertEqual(tasks[0].hours_required, 40)
        self.assertEqual(tasks[0].project_id, 1)
        self.assertIsNotNone(tasks[0].assigned_employee)
        self.assertEqual(tasks[0].assigned_employee.id, 1)
        
        # Проверяем вызов
        expected_query = """
            SELECT t.id, t.title, t.description, t.status, t.hours_required, 
                   t.employee_id, t.project_id, e.name as employee_name,
                   p.title as project_title
            FROM tasks t
            LEFT JOIN employees e ON t.employee_id = e.id
            LEFT JOIN projects p ON t.project_id = p.id
            ORDER BY t.id
        """
        self.mock_db.execute_query.assert_called_once_with(
            expected_query.strip(),
            fetch=True
        )
    
    def test_get_all_projects(self):
        """Тест получения всех проектов"""
        # Настраиваем моки для проектов
        self.mock_db.execute_query.side_effect = [
            self.test_project_data,  # Первый вызов: проекты
            [],  # Второй вызов: задачи для первого проекта
            []   # Третий вызов: задачи для второго проекта
        ]
        
        # Вызываем метод
        projects = self.db_manager.get_all_projects()
        
        # Проверяем результаты
        self.assertEqual(len(projects), 2)
        
        # Проверяем первый проект
        self.assertEqual(projects[0].id, 1)
        self.assertEqual(projects[0].title, 'Проект 1')
        self.assertEqual(len(projects[0].tasks), 0)
        
        # Проверяем второй проект
        self.assertEqual(projects[1].id, 2)
        self.assertEqual(projects[1].title, 'Проект 2')
        self.assertEqual(len(projects[1].tasks), 0)
        
        # Проверяем вызовы
        expected_calls = [
            call("SELECT id, title FROM projects ORDER BY id", fetch=True),
            call("""
                SELECT id, title, description, status, hours_required, employee_id
                FROM tasks WHERE project_id = %s
            """.strip(), (1,), fetch=True),
            call("""
                SELECT id, title, description, status, hours_required, employee_id
                FROM tasks WHERE project_id = %s
            """.strip(), (2,), fetch=True)
        ]
        self.mock_db.execute_query.assert_has_calls(expected_calls)
    
    def test_add_task(self):
        """Тест добавления задачи"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = [(10,)]  # Возвращаемый ID
        
        # Создаем задачу с сотрудником
        employee = Employee('Иван Иванов', 'Разработчик', 100000, emp_id=1)
        task = Task('Новая задача', 'Описание', 'В процессе', 
                   assigned_employee=employee, hours_required=30, project_id=1)
        
        # Вызываем метод
        result = self.db_manager.add_task(task)
        
        # Проверяем результаты
        self.assertEqual(result, 10)
        self.assertEqual(task.id, 10)
        
        # Проверяем вызов
        self.mock_db.execute_query.assert_called_once_with(
            """
            INSERT INTO tasks (title, description, status, hours_required, 
                              employee_id, project_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """.strip(),
            ('Новая задача', 'Описание', 'В процессе', 30, 1, 1),
            fetch=True
        )
    
    def test_add_task_no_employee(self):
        """Тест добавления задачи без сотрудника"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = [(10,)]
        
        # Создаем задачу без сотрудника
        task = Task('Новая задача', 'Описание', 'В процессе', 
                   hours_required=30, project_id=1)
        
        # Вызываем метод
        result = self.db_manager.add_task(task)
        
        # Проверяем результаты
        self.assertEqual(result, 10)
        
        # Проверяем вызов
        self.mock_db.execute_query.assert_called_once_with(
            """
            INSERT INTO tasks (title, description, status, hours_required, 
                              employee_id, project_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """.strip(),
            ('Новая задача', 'Описание', 'В процессе', 30, None, 1),
            fetch=True
        )
    
    def test_mark_task_complete(self):
        """Тест отметки задачи как выполненной"""
        # Настраиваем мок
        self.mock_db.execute_query.side_effect = [
            [(1, 40)],  # Первый вызов: получение employee_id и hours_required
            None        # Второй вызов: обновление статуса
        ]
        
        # Вызываем метод
        employee_id, hours = self.db_manager.mark_task_complete(1)
        
        # Проверяем результаты
        self.assertEqual(employee_id, 1)
        self.assertEqual(hours, 40)
        
        # Проверяем вызовы
        expected_calls = [
            call("SELECT employee_id, hours_required FROM tasks WHERE id = %s", (1,), fetch=True),
            call("UPDATE tasks SET status = 'Завершено' WHERE id = %s", (1,), fetch=False)
        ]
        self.mock_db.execute_query.assert_has_calls(expected_calls)
    
    def test_mark_task_complete_no_employee(self):
        """Тест отметки задачи как выполненной (без сотрудника)"""
        # Настраиваем мок
        self.mock_db.execute_query.side_effect = [
            [(None, 40)],  # Первый вызов: employee_id = None
            None           # Второй вызов: обновление статуса
        ]
        
        # Вызываем метод
        employee_id, hours = self.db_manager.mark_task_complete(1)
        
        # Проверяем результаты
        self.assertIsNone(employee_id)
        self.assertEqual(hours, 0)
    
    def test_get_tasks_by_employee(self):
        """Тест получения задач сотрудника"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = [
            (1, 'Задача 1', 'В процессе', 40),
            (2, 'Задача 2', 'Завершено', 20)
        ]
        
        # Вызываем метод без фильтра
        tasks = self.db_manager.get_tasks_by_employee(1)
        
        # Проверяем результаты
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0][0], 1)  # ID задачи
        self.assertEqual(tasks[0][1], 'Задача 1')  # Название
        self.assertEqual(tasks[0][2], 'В процессе')  # Статус
        self.assertEqual(tasks[0][3], 40)  # Часы
        
        # Проверяем вызов
        expected_query = """
                SELECT id, title, status, hours_required 
                FROM tasks 
                WHERE employee_id = %s
            """
        self.mock_db.execute_query.assert_called_once_with(
            expected_query.strip(),
            (1,),
            fetch=True
        )
    
    def test_get_tasks_by_employee_with_status(self):
        """Тест получения задач сотрудника с фильтром по статусу"""
        # Настраиваем мок
        self.mock_db.execute_query.return_value = [
            (2, 'Задача 2', 'Завершено', 20)
        ]
        
        # Вызываем метод с фильтром
        tasks = self.db_manager.get_tasks_by_employee(1, "Завершено")
        
        # Проверяем результаты
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][2], 'Завершено')
        
        # Проверяем вызов
        expected_query = """
                SELECT id, title, status, hours_required 
                FROM tasks 
                WHERE employee_id = %s AND status = %s
            """
        self.mock_db.execute_query.assert_called_once_with(
            expected_query.strip(),
            (1, "Завершено"),
            fetch=True
        )


if __name__ == '__main__':
    unittest.main()