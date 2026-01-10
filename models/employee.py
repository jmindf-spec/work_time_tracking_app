"""
Модель сотрудника
"""

class Employee:
    def __init__(self, name, position, salary, hours_worked=0, emp_id=None):
        self.id = emp_id
        self.name = name
        self.position = position
        self.salary = float(salary)
        self.hours_worked = float(hours_worked)
    
    def calculate_pay(self):
        hourly_rate = self.salary / 160
        return hourly_rate * self.hours_worked
    
    def update_hours_worked(self, db_connection):
        query = """
            SELECT COALESCE(SUM(hours_required), 0) 
            FROM tasks 
            WHERE employee_id = %s AND status = 'Завершено'
        """
        result = db_connection.execute_query(query, (self.id,), fetch=True)
        if result:
            self.hours_worked = float(result[0][0])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'salary': self.salary,
            'hours_worked': self.hours_worked
        }