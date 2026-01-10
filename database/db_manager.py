"""
Менеджер БД для работы с данными
"""

from database.db_connection import DatabaseConnection
from models import Employee, Task, Project

class DatabaseManager:
    """Менеджер для операций с БД, связанных с данными"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    # Методы для сотрудников
    def get_all_employees(self):
        query = "SELECT id, name, position, salary FROM employees ORDER BY id"
        rows = self.db.execute_query(query, fetch=True)
        employees = []
        for row in rows:
            emp = Employee(row[1], row[2], row[3], 0, row[0])
            emp.update_hours_worked(self.db)
            employees.append(emp)
        return employees
    
    def get_employee_by_id(self, emp_id):
        query = "SELECT id, name, position, salary FROM employees WHERE id = %s"
        result = self.db.execute_query(query, (emp_id,), fetch=True)
        if result:
            row = result[0]
            emp = Employee(row[1], row[2], row[3], 0, row[0])
            emp.update_hours_worked(self.db)
            return emp
        return None
    
    def get_employee_hours_worked(self, emp_id):
        query = """
            SELECT COALESCE(SUM(hours_required), 0) 
            FROM tasks 
            WHERE employee_id = %s AND status = 'Завершено'
        """
        result = self.db.execute_query(query, (emp_id,), fetch=True)
        return float(result[0][0]) if result else 0.0
    
    def add_employee(self, employee):
        query = """
            INSERT INTO employees (name, position, salary)
            VALUES (%s, %s, %s) RETURNING id
        """
        result = self.db.execute_query(query, (employee.name, employee.position, 
                                               employee.salary), fetch=True)
        if result:
            employee.id = result[0][0]
            return employee.id
        return None
    
    def update_employee(self, employee):
        query = """
            UPDATE employees 
            SET name = %s, position = %s, salary = %s
            WHERE id = %s
        """
        self.db.execute_query(query, (employee.name, employee.position, 
                                      employee.salary, employee.id))
    
    def delete_employee(self, emp_id):
        query = "DELETE FROM employees WHERE id = %s"
        self.db.execute_query(query, (emp_id,))
    
    def update_employee_hours(self, emp_id):
        """Обновляет поле hours_worked у сотрудника в БД"""
        hours = self.get_employee_hours_worked(emp_id)
        query = "UPDATE employees SET hours_worked = %s WHERE id = %s"
        self.db.execute_query(query, (hours, emp_id))
    
    # Методы для проектов
    def get_all_projects(self):
        query = "SELECT id, title FROM projects ORDER BY id"
        rows = self.db.execute_query(query, fetch=True)
        projects = []
        for row in rows:
            project = Project(row[1], project_id=row[0])
            tasks_query = """
                SELECT id, title, description, status, hours_required, employee_id
                FROM tasks WHERE project_id = %s
            """
            task_rows = self.db.execute_query(tasks_query, (row[0],), fetch=True)
            for task_row in task_rows:
                task = Task(
                    task_row[1], task_row[2], task_row[3],
                    hours_required=task_row[4], task_id=task_row[0]
                )
                if task_row[5]:
                    task.assigned_employee = Employee("", "", 0, 0, task_row[5])
                project.add_task(task)
            projects.append(project)
        return projects
    
    def add_project(self, project):
        query = "INSERT INTO projects (title) VALUES (%s) RETURNING id"
        result = self.db.execute_query(query, (project.title,), fetch=True)
        if result:
            project.id = result[0][0]
            return project.id
        return None
    
    def update_project(self, project):
        query = "UPDATE projects SET title = %s WHERE id = %s"
        self.db.execute_query(query, (project.title, project.id))
    
    def delete_project(self, project_id):
        query = "DELETE FROM projects WHERE id = %s"
        self.db.execute_query(query, (project_id,))
    
    # Методы для задач
    def get_all_tasks(self):
        query = """
            SELECT t.id, t.title, t.description, t.status, t.hours_required, 
                   t.employee_id, t.project_id, e.name as employee_name,
                   p.title as project_title
            FROM tasks t
            LEFT JOIN employees e ON t.employee_id = e.id
            LEFT JOIN projects p ON t.project_id = p.id
            ORDER BY t.id
        """
        rows = self.db.execute_query(query, fetch=True)
        tasks = []
        for row in rows:
            task = Task(
                row[1], row[2], row[3],
                hours_required=row[4], task_id=row[0]
            )
            if row[5]:
                task.assigned_employee = Employee(row[7] or "", "", 0, 0, row[5])
            task.project_id = row[6]
            tasks.append(task)
        return tasks
    
    def add_task(self, task):
        query = """
            INSERT INTO tasks (title, description, status, hours_required, 
                              employee_id, project_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """
        emp_id = task.assigned_employee.id if task.assigned_employee else None
        result = self.db.execute_query(query, (
            task.title, task.description, task.status,
            task.hours_required, emp_id, task.project_id
        ), fetch=True)
        if result:
            task.id = result[0][0]
            return task.id
        return None
    
    def update_task(self, task):
        query = """
            UPDATE tasks 
            SET title = %s, description = %s, status = %s, 
                hours_required = %s, employee_id = %s, project_id = %s
            WHERE id = %s
        """
        emp_id = task.assigned_employee.id if task.assigned_employee else None
        self.db.execute_query(query, (
            task.title, task.description, task.status,
            task.hours_required, emp_id, task.project_id, task.id
        ))
    
    def delete_task(self, task_id):
        query = "DELETE FROM tasks WHERE id = %s"
        self.db.execute_query(query, (task_id,))
    
    def mark_task_complete(self, task_id):
        """Отмечает задачу как завершенную и обновляет часы сотрудника"""
        query = "SELECT employee_id, hours_required FROM tasks WHERE id = %s"
        result = self.db.execute_query(query, (task_id,), fetch=True)
        
        if result and result[0][0]:
            employee_id = result[0][0]
            hours = result[0][1] or 0
            
            update_query = "UPDATE tasks SET status = 'Завершено' WHERE id = %s"
            self.db.execute_query(update_query, (task_id,))
            
            return employee_id, hours
        else:
            update_query = "UPDATE tasks SET status = 'Завершено' WHERE id = %s"
            self.db.execute_query(update_query, (task_id,))
            return None, 0
    
    def get_tasks_by_employee(self, emp_id, status=None):
        """Получает задачи сотрудника с возможностью фильтрации по статусу"""
        if status:
            query = """
                SELECT id, title, status, hours_required 
                FROM tasks 
                WHERE employee_id = %s AND status = %s
            """
            result = self.db.execute_query(query, (emp_id, status), fetch=True)
        else:
            query = """
                SELECT id, title, status, hours_required 
                FROM tasks 
                WHERE employee_id = %s
            """
            result = self.db.execute_query(query, (emp_id,), fetch=True)
        return result if result else []
    
    def get_task_project_title(self, task_id):
        """Получить название проекта по ID задачи"""
        if not task_id:
            return "Не назначен"
        query = """
            SELECT p.title 
            FROM tasks t 
            LEFT JOIN projects p ON t.project_id = p.id 
            WHERE t.id = %s
        """
        result = self.db.execute_query(query, (task_id,), fetch=True)
        return result[0][0] if result else "Не назначен"
    
    def get_project_title(self, project_id):
        """Получить название проекта по ID"""
        if not project_id:
            return "Не назначен"
        query = "SELECT title FROM projects WHERE id = %s"
        result = self.db.execute_query(query, (project_id,), fetch=True)
        return result[0][0] if result else "Неизвестно"