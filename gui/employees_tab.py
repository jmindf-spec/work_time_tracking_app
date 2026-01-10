"""
Вкладка для работы с сотрудниками
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd
from models import Employee
from utils import export_to_csv

class EmployeesTab:
    def __init__(self, parent, db_manager, app):
        self.parent = parent
        self.db_manager = db_manager
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки сотрудников"""
        # Верхняя панель с кнопками
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Добавить", 
                  command=self.add_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Редактировать", 
                  command=self.edit_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить", 
                  command=self.delete).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Показать задачи", 
                  command=self.show_tasks).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV", 
                  command=self.export_to_csv).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить", 
                  command=self.load_data).pack(side='left', padx=5)
        
        # Таблица сотрудников
        columns = ('ID', 'Имя', 'Должность', 'Зарплата', 'Отработано часов', 'Заработок', 'Завершено задач')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", 
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=5, pady=5)
    
    def load_data(self):
        """Загрузка данных сотрудников"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        employees = self.db_manager.get_all_employees()
        for emp in employees:
            pay = emp.calculate_pay()
            
            completed_tasks = self.db_manager.get_tasks_by_employee(emp.id, "Завершено")
            completed_count = len(completed_tasks) if completed_tasks else 0
            
            self.tree.insert('', 'end', values=(
                emp.id, emp.name, emp.position, 
                f"{emp.salary:.2f}", f"{emp.hours_worked:.1f}",
                f"{pay:.2f}", completed_count
            ))
    
    def add_dialog(self):
        """Диалог добавления сотрудника"""
        self.employee_dialog("Добавить сотрудника", None)
    
    def edit_dialog(self):
        """Диалог редактирования сотрудника"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для редактирования")
            return
        
        item = self.tree.item(selection[0])
        emp_id = item['values'][0]       
        employee = self.db_manager.get_employee_by_id(emp_id)
        if employee:
            self.employee_dialog("Редактировать сотрудника", employee)
    
    def employee_dialog(self, title, employee):
        """Общий диалог для добавления/редактирования сотрудника"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title(title)
        dialog.geometry("400x300")
        
        current_hours = self.db_manager.get_employee_hours_worked(employee.id) if employee else 0
        
        ttk.Label(dialog, text="Имя:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        name_var = tk.StringVar(value=employee.name if employee else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Должность:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        position_var = tk.StringVar(value=employee.position if employee else "")
        position_entry = ttk.Entry(dialog, textvariable=position_var, width=30)
        position_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Зарплата:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        salary_var = tk.StringVar(value=str(employee.salary) if employee else "0")
        salary_entry = ttk.Entry(dialog, textvariable=salary_var, width=30)
        salary_entry.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text=f"Отработано часов (авто):").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        ttk.Label(dialog, text=f"{current_hours:.1f} ч").grid(row=3, column=1, padx=10, pady=10, sticky='w')
        
        def save_employee():
            try:
                name = name_var.get()
                position = position_var.get()
                salary = float(salary_var.get())
                
                if not name:
                    messagebox.showerror("Ошибка", "Введите имя сотрудника")
                    return
                
                if employee:
                    employee.name = name
                    employee.position = position
                    employee.salary = salary
                    self.db_manager.update_employee(employee)
                else:
                    new_employee = Employee(name, position, salary, 0)
                    self.db_manager.add_employee(new_employee)
                
                self.load_data()
                dialog.destroy()
                messagebox.showinfo("Успех", "Сотрудник сохранен")
                
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректные числовые значения")
        
        ttk.Button(dialog, text="Сохранить", command=save_employee).grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=5, column=0, columnspan=2)
    
    def delete(self):
        """Удаление сотрудника"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранного сотрудника?"):
            item = self.tree.item(selection[0])
            emp_id = item['values'][0]
            self.db_manager.delete_employee(emp_id)
            self.load_data()
            self.app.tasks_tab.load_data()
    
    def show_tasks(self):
        """Показать задачи сотрудника"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника")
            return
        
        item = self.tree.item(selection[0])
        emp_id = item['values'][0]
        emp_name = item['values'][1]
        
        tasks = self.db_manager.get_tasks_by_employee(emp_id)
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Задачи сотрудника: {emp_name}")
        dialog.geometry("600x400")
        
        columns = ('ID', 'Название', 'Статус', 'Часы', 'Проект')
        tree = ttk.Treeview(dialog, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        completed_hours = 0
        for task in tasks:
            task_id, title, status, hours = task
            project_title = self.db_manager.get_task_project_title(task_id)
            
            tree.insert('', 'end', values=(
                task_id, title, status, f"{hours:.1f}", project_title
            ))
            
            if status == "Завершено":
                completed_hours += hours
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        stats_frame = ttk.Frame(dialog)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t[2] == "Завершено")
        
        ttk.Label(stats_frame, text=f"Всего задач: {total_tasks}").pack(side='left', padx=10)
        ttk.Label(stats_frame, text=f"Завершено: {completed_tasks}").pack(side='left', padx=10)
        ttk.Label(stats_frame, text=f"Отработано часов: {completed_hours:.1f}").pack(side='left', padx=10)
    
    def export_to_csv(self):
        """Экспорт сотрудников в CSV"""
        employees = self.db_manager.get_all_employees()
        data = []
        for emp in employees:
            completed_tasks = self.db_manager.get_tasks_by_employee(emp.id, "Завершено")
            completed_count = len(completed_tasks) if completed_tasks else 0
            
            data.append({
                'ID': emp.id,
                'Имя': emp.name,
                'Должность': emp.position,
                'Зарплата': emp.salary,
                'Отработано часов': emp.hours_worked,
                'Заработок': emp.calculate_pay(),
                'Завершено задач': completed_count
            })
        
        df = pd.DataFrame(data)
        filename = export_to_csv(df, "employees")
        messagebox.showinfo("Экспорт", f"Данные экспортированы в {filename}")