"""
Модель задачи
"""

class Task:
    def __init__(self, title, description, status="В процессе", assigned_employee=None,
                 hours_required=0, project_id=None, task_id=None):
        self.id = task_id
        self.title = title
        self.description = description
        self.status = status
        self.assigned_employee = assigned_employee
        self.hours_required = float(hours_required) if hours_required else 0.0
        self.project_id = project_id
    
    def mark_complete(self):
        old_status = self.status
        self.status = "Завершено"
        return old_status != "Завершено"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'hours_required': self.hours_required,
            'employee_id': self.assigned_employee.id if self.assigned_employee else None,
            'project_id': self.project_id
        }