"""
Тесты для моделей данных
"""

import unittest
import sys
import os

# Добавляем путь к проекту для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.employee import Employee
from models.task import Task
from models.project import Project

class TestEmployee(unittest.TestCase):
    """Тесты для класса Employee"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.employee = Employee(
            name="Иван Иванов",
            position="Разработчик",
            salary=100000,
            hours_worked=40,
            emp_id=1
        )
    
    def test_employee_creation(self):
        """Тест создания сотрудника"""
        self.assertEqual(self.employee.name, "Иван Иванов")
        self.assertEqual(self.employee.position, "Разработчик")
        self.assertEqual(self.employee.salary, 100000)
        self.assertEqual(self.employee.hours_worked, 40)
        self.assertEqual(self.employee.id, 1)
    
    def test_calculate_pay(self):
        """Тест расчета заработной платы"""
        # При 160 рабочих часах в месяц, часовая ставка = 100000 / 160 = 625
        # За 40 часов: 625 * 40 = 25000
        expected_pay = (100000 / 160) * 40
        self.assertEqual(self.employee.calculate_pay(), expected_pay)
    
    def test_employee_to_dict(self):
        """Тест преобразования сотрудника в словарь"""
        employee_dict = self.employee.to_dict()
        self.assertEqual(employee_dict['name'], "Иван Иванов")
        self.assertEqual(employee_dict['position'], "Разработчик")
        self.assertEqual(employee_dict['salary'], 100000)
        self.assertEqual(employee_dict['hours_worked'], 40)
        self.assertEqual(employee_dict['id'], 1)
    
    def test_employee_with_default_values(self):
        """Тест создания сотрудника с значениями по умолчанию"""
        employee = Employee("Петр Петров", "Менеджер", 80000)
        self.assertEqual(employee.name, "Петр Петров")
        self.assertEqual(employee.position, "Менеджер")
        self.assertEqual(employee.salary, 80000)
        self.assertEqual(employee.hours_worked, 0)
        self.assertIsNone(employee.id)


class TestTask(unittest.TestCase):
    """Тесты для класса Task"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.employee = Employee("Иван Иванов", "Разработчик", 100000, emp_id=1)
        self.task = Task(
            title="Разработка API",
            description="Разработать REST API",
            status="В процессе",
            assigned_employee=self.employee,
            hours_required=40,
            project_id=1,
            task_id=1
        )
    
    def test_task_creation(self):
        """Тест создания задачи"""
        self.assertEqual(self.task.title, "Разработка API")
        self.assertEqual(self.task.description, "Разработать REST API")
        self.assertEqual(self.task.status, "В процессе")
        self.assertEqual(self.task.assigned_employee, self.employee)
        self.assertEqual(self.task.hours_required, 40)
        self.assertEqual(self.task.project_id, 1)
        self.assertEqual(self.task.id, 1)
    
    def test_mark_complete(self):
        """Тест отметки задачи как выполненной"""
        # Проверяем начальный статус
        self.assertEqual(self.task.status, "В процессе")
        
        # Отмечаем как выполненную
        changed = self.task.mark_complete()
        
        # Проверяем что статус изменился
        self.assertTrue(changed)
        self.assertEqual(self.task.status, "Завершено")
        
        # Пробуем отметить снова
        changed_again = self.task.mark_complete()
        
        # Статус уже был "Завершено", поэтому не должен измениться
        self.assertFalse(changed_again)
        self.assertEqual(self.task.status, "Завершено")
    
    def test_task_to_dict(self):
        """Тест преобразования задачи в словарь"""
        task_dict = self.task.to_dict()
        self.assertEqual(task_dict['title'], "Разработка API")
        self.assertEqual(task_dict['description'], "Разработать REST API")
        self.assertEqual(task_dict['status'], "В процессе")
        self.assertEqual(task_dict['hours_required'], 40)
        self.assertEqual(task_dict['employee_id'], 1)
        self.assertEqual(task_dict['project_id'], 1)
        self.assertEqual(task_dict['id'], 1)
    
    def test_task_without_assignment(self):
        """Тест создания задачи без назначенного сотрудника"""
        task = Task("Тестовая задача", "Описание", "В процессе")
        self.assertEqual(task.title, "Тестовая задача")
        self.assertIsNone(task.assigned_employee)
        self.assertEqual(task.hours_required, 0.0)
        self.assertIsNone(task.project_id)
        self.assertIsNone(task.id)


class TestProject(unittest.TestCase):
    """Тесты для класса Project"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.project = Project(
            title="Разработка веб-сайта",
            project_id=1
        )
        
        # Создаем тестовые задачи
        self.task1 = Task("Дизайн", "Создать дизайн", "Завершено", hours_required=20)
        self.task2 = Task("Верстка", "Сверстать страницы", "В процессе", hours_required=30)
        self.task3 = Task("Тестирование", "Протестировать функционал", "В процессе", hours_required=10)
        
        # Добавляем задачи в проект
        self.project.add_task(self.task1)
        self.project.add_task(self.task2)
        self.project.add_task(self.task3)
    
    def test_project_creation(self):
        """Тест создания проекта"""
        self.assertEqual(self.project.title, "Разработка веб-сайта")
        self.assertEqual(self.project.id, 1)
        self.assertEqual(len(self.project.tasks), 3)
    
    def test_add_task(self):
        """Тест добавления задачи в проект"""
        # Проверяем что задачи добавлены
        self.assertIn(self.task1, self.project.tasks)
        self.assertIn(self.task2, self.project.tasks)
        self.assertIn(self.task3, self.project.tasks)
        
        # Проверяем что у задачи установлен project_id
        self.assertEqual(self.task1.project_id, 1)
        self.assertEqual(self.task2.project_id, 1)
        self.assertEqual(self.task3.project_id, 1)
    
    def test_project_progress(self):
        """Тест расчета прогресса проекта"""
        # Из 3 задач только 1 завершена = 33.33%
        expected_progress = (1 / 3) * 100
        self.assertAlmostEqual(self.project.project_progress(), expected_progress, places=2)
    
    def test_project_progress_empty(self):
        """Тест прогресса пустого проекта"""
        empty_project = Project("Пустой проект")
        self.assertEqual(empty_project.project_progress(), 0)
    
    def test_project_to_dict(self):
        """Тест преобразования проекта в словарь"""
        project_dict = self.project.to_dict()
        self.assertEqual(project_dict['title'], "Разработка веб-сайта")
        self.assertEqual(project_dict['id'], 1)
        self.assertEqual(project_dict['total_tasks'], 3)
        self.assertEqual(project_dict['completed_tasks'], 1)
        self.assertEqual(project_dict['progress'], "33.3%")  # Округление до одного знака
    
    def test_project_without_tasks(self):
        """Тест проекта без задач"""
        project = Project("Простой проект")
        project_dict = project.to_dict()
        self.assertEqual(project_dict['total_tasks'], 0)
        self.assertEqual(project_dict['completed_tasks'], 0)
        self.assertEqual(project_dict['progress'], "0.0%")


if __name__ == '__main__':
    unittest.main()