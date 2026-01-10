"""
GUI модули приложения
"""

from .main_window import TimeTrackingApp
from .employees_tab import EmployeesTab
from .tasks_tab import TasksTab
from .projects_tab import ProjectsTab
from .data_tab import DataTab

__all__ = [
    'TimeTrackingApp',
    'EmployeesTab',
    'TasksTab',
    'ProjectsTab',
    'DataTab'
]
