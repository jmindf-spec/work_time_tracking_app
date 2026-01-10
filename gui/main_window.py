"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config

# Импортируем напрямую из модулей
try:
    from database.db_connection_gui import DatabaseConnectionManager
    from database.db_manager import DatabaseManager
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    # Альтернативный импорт
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from database.db_connection_gui import DatabaseConnectionManager
    from database.db_manager import DatabaseManager

# Импорт вкладок
from gui.employees_tab import EmployeesTab
from gui.tasks_tab import TasksTab
from gui.projects_tab import ProjectsTab
from gui.data_tab import DataTab

class TimeTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.root.geometry(config.DEFAULT_WINDOW_SIZE)
        
        # Инициализация менеджера подключения к БД
        self.connection_manager = DatabaseConnectionManager(root)
        
        # Попытка подключения к БД
        self.db_connection = self.connection_manager.create_connection()
        if not self.db_connection:
            # Если не удалось подключиться, закрываем приложение
            self.root.destroy()
            return
        
        # Инициализация менеджера БД
        self.db_manager = DatabaseManager(self.db_connection)
        
        # Инициализация GUI компонентов
        self.setup_ui()
        self.load_data()
        
        # Создание меню ПОСЛЕ инициализации всех компонентов
        self.setup_menu()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создание вкладок
        self.employees_tab = EmployeesTab(
            self.notebook, self.db_manager, self
        )
        self.tasks_tab = TasksTab(
            self.notebook, self.db_manager, self
        )
        self.projects_tab = ProjectsTab(
            self.notebook, self.db_manager, self
        )
        self.data_tab = DataTab(
            self.notebook, self.db_manager, self
        )
        
        # Добавление вкладок
        self.notebook.add(self.employees_tab.frame, text='Сотрудники')
        self.notebook.add(self.tasks_tab.frame, text='Задачи')
        self.notebook.add(self.projects_tab.frame, text='Проекты')
        self.notebook.add(self.data_tab.frame, text='Работа с данными')
    
    def setup_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Подключение к БД...", 
                            command=self.connection_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню Данные
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Данные", menu=data_menu)
        data_menu.add_command(label="Обновить все данные", 
                            command=self.load_data)
        data_menu.add_separator()
        data_menu.add_command(label="Экспорт сотрудников в CSV", 
                            command=self.employees_tab.export_to_csv)
        data_menu.add_command(label="Экспорт задач в CSV", 
                            command=self.tasks_tab.export_to_csv)
        data_menu.add_command(label="Экспорт проектов в CSV", 
                            command=self.projects_tab.export_to_csv)
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # Сохраняем ссылку на меню
        self.menubar = menubar
    
    def connection_dialog(self):
        """Открыть диалог подключения к БД"""
        if self.connection_manager.show_connection_dialog(self.reconnect_callback):
            messagebox.showinfo("Успех", "Подключение к БД обновлено")
    
    def reconnect_callback(self, new_config):
        """Обратный вызов после успешного подключения"""
        if self.db_connection:
            self.db_connection.disconnect()
        
        self.db_connection = self.connection_manager.create_connection(new_config)
        if self.db_connection:
            self.db_manager = DatabaseManager(self.db_connection)
            self.load_data()
        else:
            messagebox.showerror("Ошибка", "Не удалось переподключиться к базе данных")
    
    def load_data(self):
        """Загрузка всех данных"""
        self.employees_tab.load_data()
        self.tasks_tab.load_data()
        self.projects_tab.load_data()
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = f"""
{config.APP_NAME}
Версия {config.APP_VERSION}

Система учета рабочего времени и задач
Итоговая аттестация
"""
        messagebox.showinfo("О программе", about_text)