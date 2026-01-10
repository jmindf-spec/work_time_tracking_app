"""
Модель проекта
"""

class Project:
    def __init__(self, title, tasks=None, project_id=None):
        self.id = project_id
        self.title = title
        self.tasks = tasks or []
    
    def add_task(self, task):
        self.tasks.append(task)
        task.project_id = self.id
    
    def project_progress(self):
        if not self.tasks:
            return 0
        completed = sum(1 for task in self.tasks if task.status == "Завершено")
        return (completed / len(self.tasks)) * 100
    
    def to_dict(self):
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task.status == "Завершено")
        progress = self.project_progress()
        
        return {
            'id': self.id,
            'title': self.title,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress': f"{progress:.1f}%"
        }