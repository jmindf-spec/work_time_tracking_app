"""
Вкладка для работы с данными
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import pandas as pd
import numpy as np
from utils import extract_emails, clean_csv_data, get_csv_stats, save_cleaned_csv

class DataTab:
    def __init__(self, parent, db_manager, app):
        self.parent = parent
        self.db_manager = db_manager
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки работы с данными"""
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Фрейм для поиска email
        email_frame = ttk.LabelFrame(main_frame, text="Извлечение email-адресов")
        email_frame.pack(fill='x', pady=10)
        
        # Панель с кнопками для email
        email_buttons_frame = ttk.Frame(email_frame)
        email_buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(email_frame, text="Введите текст:").pack(anchor='w', padx=5, pady=5)
        self.email_text = tk.Text(email_frame, height=5, width=80)
        self.email_text.pack(padx=5, pady=5)
        
        ttk.Button(email_buttons_frame, text="Извлечь email", 
                  command=self.extract_emails).pack(side='left', padx=5)
        ttk.Button(email_buttons_frame, text="Очистить", 
                  command=self.clear_email_fields).pack(side='left', padx=5)
        
        ttk.Label(email_frame, text="Результат:").pack(anchor='w', padx=5, pady=(10, 0))
        self.email_result = tk.Text(email_frame, height=5, width=80, state='disabled')
        self.email_result.pack(padx=5, pady=5)
        
        # Фрейм для работы с CSV
        csv_frame = ttk.LabelFrame(main_frame, text="Работа с CSV файлами")
        csv_frame.pack(fill='x', pady=10)
        
        # Панель для выбора файла
        file_selection_frame = ttk.Frame(csv_frame)
        file_selection_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(file_selection_frame, text="Путь к CSV файлу:").pack(side='left', padx=5)
        self.csv_path = ttk.Entry(file_selection_frame, width=60)
        self.csv_path.pack(side='left', padx=5, expand=True, fill='x')
        
        ttk.Button(file_selection_frame, text="Открыть файл", 
                  command=self.browse_csv_file).pack(side='left', padx=5)
        
        # Панель с кнопками для CSV
        csv_buttons_frame = ttk.Frame(csv_frame)
        csv_buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(csv_buttons_frame, text="Загрузить и сохранить CSV", 
                  command=self.load_and_save_csv).pack(side='left', padx=5)
        ttk.Button(csv_buttons_frame, text="Очистить", 
                  command=self.clear_csv_fields).pack(side='left', padx=5)
        
        ttk.Label(csv_frame, text="Результат обработки:").pack(anchor='w', padx=5, pady=(10, 0))
        self.csv_result = tk.Text(csv_frame, height=10, width=80, state='disabled')
        self.csv_result.pack(padx=5, pady=5)
    
    def clear_email_fields(self):
        """Очистка полей email"""
        self.email_text.delete('1.0', 'end')
        self.email_result.config(state='normal')
        self.email_result.delete('1.0', 'end')
        self.email_result.config(state='disabled')
    
    def browse_csv_file(self):
        """Выбор CSV файла"""
        filepath = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            self.csv_path.delete(0, 'end')
            self.csv_path.insert(0, filepath)
    
    def clear_csv_fields(self):
        """Очистка полей CSV"""
        self.csv_path.delete(0, 'end')
        self.csv_result.config(state='normal')
        self.csv_result.delete('1.0', 'end')
        self.csv_result.config(state='disabled')
    
    def extract_emails(self):
        """Извлечение email из текста"""
        text = self.email_text.get('1.0', 'end-1c')
        emails = extract_emails(text)
        
        self.email_result.config(state='normal')
        self.email_result.delete('1.0', 'end')
        
        if emails:
            self.email_result.insert('1.0', 'Найденные email-адреса:\n\n')
            for email in emails:
                self.email_result.insert('end', f'{email}\n')
        else:
            self.email_result.insert('1.0', 'Email-адреса не найдены')
        
        self.email_result.config(state='disabled')
    
    def load_and_save_csv(self):
        """Загрузка и обработка CSV файла"""
        filepath = self.csv_path.get()
        if not filepath:
            messagebox.showwarning("Предупреждение", "Выберите CSV файл")
            return
        
        try:
            df_original = pd.read_csv(filepath)
            stats = get_csv_stats(df_original)
            
            df_cleaned = clean_csv_data(df_original)
            cleaned_file_path = save_cleaned_csv(df_cleaned, filepath)
            
            self.csv_result.config(state='normal')
            self.csv_result.delete('1.0', 'end')
            
            self.csv_result.insert('1.0', f"Исходный файл: {filepath}\n")
            self.csv_result.insert('end', f"Очищенный файл: {cleaned_file_path}\n\n")
            self.csv_result.insert('end', f"Записей в исходном файле: {stats['total_rows']}\n")
            self.csv_result.insert('end', f"Записей после удаления пустых значений: {len(df_cleaned)}\n")
            self.csv_result.insert('end', f"Удалено записей: {stats['total_rows'] - len(df_cleaned)}\n\n")
            
            if stats['total_missing'] > 0:
                self.csv_result.insert('end', "Статистика по пропущенным значениям:\n")
                for column, count in stats['missing_values'].items():
                    if count > 0:
                        self.csv_result.insert('end', f"  {column}: {count} пропущенных значений\n")
            
            self.csv_result.insert('end', f"\nКолонки: {', '.join(df_cleaned.columns)}\n\n")
            self.csv_result.insert('end', "Первые 10 строк очищенного файла:\n")
            self.csv_result.insert('end', df_cleaned.head(10).to_string())
            
            self.csv_result.config(state='disabled')
            
            messagebox.showinfo(
                "Успех", 
                f"Файл успешно обработан!\n\n"
                f"Исходный файл: {stats['total_rows']} записей\n"
                f"Очищенный файл: {len(df_cleaned)} записей\n"
                f"Удалено записей с пустыми значениями: {stats['total_rows'] - len(df_cleaned)}\n\n"
                f"Сохранен как: {cleaned_file_path}"
            )
            
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл не найден: {filepath}")
        except pd.errors.EmptyDataError:
            messagebox.showerror("Ошибка", "Файл пуст или имеет неверный формат")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обработать CSV файл: {e}")