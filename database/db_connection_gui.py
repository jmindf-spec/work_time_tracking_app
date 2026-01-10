"""
GUI для настройки подключения к БД
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
from .db_connection import DatabaseConnection

class DatabaseConnectionDialog:
    """Диалоговое окно для настройки подключения к БД"""
    
    def __init__(self, parent, db_config=None, callback=None):
        self.parent = parent
        self.db_config = db_config or config.DEFAULT_DB_CONFIG
        self.callback = callback  # Функция обратного вызова после успешного подключения
        self.connection_result = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Создание интерфейса диалогового окна"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Подключение к базе данных")
        self.dialog.geometry("500x450")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Центрирование окна
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_reqwidth()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_reqheight()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Основной фрейм
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Настройки подключения к PostgreSQL", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Поля для ввода
        row = 1
        
        # Хост
        ttk.Label(main_frame, text="Хост:").grid(row=row, column=0, sticky='w', pady=5)
        self.host_var = tk.StringVar(value=self.db_config["host"])
        host_entry = ttk.Entry(main_frame, textvariable=self.host_var, width=40)
        host_entry.grid(row=row, column=1, pady=5, padx=(10, 0), sticky='ew')
        row += 1
        
        # Порт
        ttk.Label(main_frame, text="Порт:").grid(row=row, column=0, sticky='w', pady=5)
        self.port_var = tk.StringVar(value=self.db_config.get("port", "5432"))
        port_entry = ttk.Entry(main_frame, textvariable=self.port_var, width=40)
        port_entry.grid(row=row, column=1, pady=5, padx=(10, 0), sticky='ew')
        row += 1
        
        # База данных
        ttk.Label(main_frame, text="База данных:").grid(row=row, column=0, sticky='w', pady=5)
        self.database_var = tk.StringVar(value=self.db_config["database"])
        database_entry = ttk.Entry(main_frame, textvariable=self.database_var, width=40)
        database_entry.grid(row=row, column=1, pady=5, padx=(10, 0), sticky='ew')
        row += 1
        
        # Пользователь
        ttk.Label(main_frame, text="Пользователь:").grid(row=row, column=0, sticky='w', pady=5)
        self.user_var = tk.StringVar(value=self.db_config["user"])
        user_entry = ttk.Entry(main_frame, textvariable=self.user_var, width=40)
        user_entry.grid(row=row, column=1, pady=5, padx=(10, 0), sticky='ew')
        row += 1
        
        # Пароль
        ttk.Label(main_frame, text="Пароль:").grid(row=row, column=0, sticky='w', pady=5)
        self.password_var = tk.StringVar(value=self.db_config["password"])
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                  width=40, show="*")
        password_entry.grid(row=row, column=1, pady=5, padx=(10, 0), sticky='ew')
        row += 1
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20, sticky='ew')
        
        # Кнопка тестирования
        ttk.Button(button_frame, text="Тестировать подключение", 
                  command=self.test_connection).pack(side='left', padx=5)
        
        # Кнопка подключения
        ttk.Button(button_frame, text="Подключиться", 
                  command=self.connect, style='Accent.TButton').pack(side='left', padx=5)
        
        # Кнопка отмены
        ttk.Button(button_frame, text="Отмена", 
                  command=self.dialog.destroy).pack(side='left', padx=5)
        
        # Метка статуса
        self.status_label = ttk.Label(
            main_frame, 
            text="", 
            foreground="gray",
            wraplength=450,
            justify="left",
            anchor="w"
        )
        self.status_label.grid(row=row+1, column=0, columnspan=2, pady=(20, 10), sticky='w')
        
        # Устанавливаем вес столбцов
        main_frame.columnconfigure(1, weight=1)
        
        # Стиль для кнопки
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        
        # Бинд на Enter
        self.dialog.bind('<Return>', lambda e: self.connect())
        
        # Фокус
        host_entry.focus_set()
    
    def truncate_error_message(self, error_msg, max_length=80):
        """Обрезает слишком длинные сообщения об ошибках"""
        if len(error_msg) > max_length:
            return error_msg[:max_length] + "..."
        return error_msg
    
    def test_connection(self):
        """Тестирование подключения с текущими параметрами"""
        config_dict = self.get_current_config()
        
        try:
            db = DatabaseConnection(config_dict)
            if db.connect():
                # Показать информацию о БД
                databases = db.get_databases()
                tables = db.get_tables()
                
                info_text = f"✓ Подключение успешно установлено\n"
                info_text += f"Базы данных: {len(databases)}, Таблицы: {len(tables)}"
                if tables:
                    table_list = ", ".join(tables[:3])
                    if len(tables) > 3:
                        info_text += f" ({table_list}...)"
                    else:
                        info_text += f" ({table_list})"
                
                self.show_status(info_text, "green")
                db.disconnect()
                return True
            else:
                self.show_status("✗ Не удалось подключиться к БД", "red")
                return False
        except Exception as e:
            error_msg = str(e)
            truncated_error = self.truncate_error_message(error_msg)
            self.show_status(f"✗ Ошибка подключения: {truncated_error}", "red")
            return False
    
    def connect(self):
        """Подключение к БД с текущими параметрами"""
        if self.test_connection():
            config_dict = self.get_current_config()
            self.connection_result = config_dict
            
            if self.callback:
                self.callback(config_dict)
            
            self.dialog.destroy()
            return True
        return False
    
    def get_current_config(self):
        """Получить текущую конфигурацию из полей ввода"""
        return {
            "host": self.host_var.get(),
            "port": self.port_var.get(),
            "database": self.database_var.get(),
            "user": self.user_var.get(),
            "password": self.password_var.get()
        }
    
    def show_status(self, message, color="black"):
        """Показать статусное сообщение"""
        self.status_label.config(text=message, foreground=color)

class DatabaseConnectionManager:
    """Менеджер для управления подключением к БД с GUI"""
    
    def __init__(self, parent):
        self.parent = parent
        self.db_connection = None
        self.db_config = None
    
    def show_connection_dialog(self, callback=None):
        """Показать диалоговое окно подключения"""
        dialog = DatabaseConnectionDialog(self.parent, self.db_config, callback)
        self.parent.wait_window(dialog.dialog)
        
        if dialog.connection_result:
            self.db_config = dialog.connection_result
            return True
        return False
    
    def create_connection(self, config_dict=None):
        """Создать подключение к БД"""
        if config_dict:
            self.db_config = config_dict
        
        if not self.db_config:
            if not self.show_connection_dialog():
                return None
        
        self.db_connection = DatabaseConnection(self.db_config)
        if self.db_connection.connect():
            return self.db_connection
        else:
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
            return None
    
    def get_connection(self):
        """Получить текущее подключение или создать новое"""
        if not self.db_connection or not self.db_connection.is_connected:
            return self.create_connection()
        return self.db_connection