"""
Вкладка для работы с задачами
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from models import Task, Employee
from utils import export_to_csv

class TasksTab:
    def __init__(self, parent, db_manager, app):
        self.parent = parent
        self.db_manager = db_manager
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки задач"""
        # Верхняя панель с кнопками
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Добавить", 
                  command=self.add_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Редактировать", 
                  command=self.edit_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить", 
                  command=self.delete).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Выполнено", 
                  command=self.mark_complete).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV", 
                  command=self.export_to_csv).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить", 
                  command=self.load_data).pack(side='left', padx=5)
        
        # Таблица задач
        columns = ('ID', 'Название', 'Статус', 'Часы', 'Сотрудник', 'Проект')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", 
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=5, pady=5)
    
    def load_data(self):
        """Загрузка данных задач"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        tasks = self.db_manager.get_all_tasks()
        for task in tasks:
            emp_name = task.assigned_employee.name if task.assigned_employee else "Не назначен"
            project_title = self.db_manager.get_project_title(task.project_id) if task.project_id else "Не назначен"
            
            self.tree.insert('', 'end', values=(
                task.id, task.title, task.status, 
                f"{task.hours_required:.1f}", emp_name, project_title
            ))
    
    def add_dialog(self):
        """Диалог добавления задачи"""
        self.task_dialog("Добавить задачу", None)
    
    def edit_dialog(self):
        """Диалог редактирования задачи"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования")
            return
        
        item = self.tree.item(selection[0])
        task_id = item['values'][0]
        
        tasks = self.db_manager.get_all_tasks()
        task = next((t for t in tasks if t.id == task_id), None)
        
        if task:
            self.task_dialog("Редактировать задачу", task)
    
    def task_dialog(self, title, task):
        """Общий диалог для добавления/редактирования задачи"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title(title)
        dialog.geometry("500x400")
        
        employees = self.db_manager.get_all_employees()
        projects = self.db_manager.get_all_projects()
        
        ttk.Label(dialog, text="Название:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        title_var = tk.StringVar(value=task.title if task else "")
        title_entry = ttk.Entry(dialog, textvariable=title_var, width=40)
        title_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Описание:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        description_text = tk.Text(dialog, height=5, width=40)
        description_text.grid(row=1, column=1, padx=10, pady=10)
        if task and task.description:
            description_text.insert('1.0', task.description)
        
        ttk.Label(dialog, text="Статус:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        status_var = tk.StringVar(value=task.status if task else "В процессе")
        status_combo = ttk.Combobox(dialog, textvariable=status_var, 
                                   values=["В процессе", "Завершено"], state="readonly")
        status_combo.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Требуется часов:").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        hours_var = tk.StringVar(value=str(task.hours_required) if task else "0")
        hours_entry = ttk.Entry(dialog, textvariable=hours_var, width=40)
        hours_entry.grid(row=3, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Сотрудник:").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        employee_var = tk.StringVar()
        employee_combo = ttk.Combobox(dialog, textvariable=employee_var, state="readonly")
        employee_combo['values'] = [f"{e.id}: {e.name}" for e in employees]
        employee_combo.grid(row=4, column=1, padx=10, pady=10)
        
        if task and task.assigned_employee:
            employee_combo.set(f"{task.assigned_employee.id}: {task.assigned_employee.name}")
        
        ttk.Label(dialog, text="Проект:").grid(row=5, column=0, padx=10, pady=10, sticky='w')
        project_var = tk.StringVar()
        project_combo = ttk.Combobox(dialog, textvariable=project_var, state="readonly")
        project_combo['values'] = [f"{p.id}: {p.title}" for p in projects]
        project_combo.grid(row=5, column=1, padx=10, pady=10)
        
        if task and task.project_id:
            for p in projects:
                if p.id == task.project_id:
                    project_combo.set(f"{p.id}: {p.title}")
                    break
        
        def save_task():
            try:
                title_val = title_var.get()
                description = description_text.get('1.0', 'end-1c')
                status = status_var.get()
                hours = float(hours_var.get())
                
                emp_id = None
                emp_obj = None
                if employee_var.get():
                    emp_id = int(employee_var.get().split(':')[0])
                    emp_obj = next((e for e in employees if e.id == emp_id), None)
                
                proj_id = None
                if project_var.get():
                    proj_id = int(project_var.get().split(':')[0])
                
                if task:
                    task.title = title_val
                    task.description = description
                    task.status = status
                    task.hours_required = hours
                    if emp_obj:
                        task.assigned_employee = emp_obj
                    task.project_id = proj_id
                    self.db_manager.update_task(task)
                else:
                    new_task = Task(title_val, description, status, 
                                   hours_required=hours)
                    if emp_obj:
                        new_task.assigned_employee = emp_obj
                    new_task.project_id = proj_id
                    self.db_manager.add_task(new_task)
                
                self.load_data()
                self.app.projects_tab.load_data()
                self.app.employees_tab.load_data()
                dialog.destroy()
                messagebox.showinfo("Успех", "Задача сохранена")
                
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректные числовые значения")
        
        ttk.Button(dialog, text="Сохранить", command=save_task).grid(row=6, column=0, columnspan=2, pady=20)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=7, column=0, columnspan=2)
    
    def delete(self):
        """Удаление задачи"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную задачу?"):
            item = self.tree.item(selection[0])
            task_id = item['values'][0]
            
            self.db_manager.delete_task(task_id)
            self.load_data()
            self.app.projects_tab.load_data()
            self.app.employees_tab.load_data()
            messagebox.showinfo("Удалено", "Задача удалена")
    
    def mark_complete(self):
        """Отметить задачу как выполненную"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для отметки как выполненную")
            return
        
        item = self.tree.item(selection[0])
        task_id = item['values'][0]
        
        employee_id, hours = self.db_manager.mark_task_complete(task_id)
        
        if employee_id:
            self.db_manager.update_employee_hours(employee_id)
            messagebox.showinfo("Выполнено", f"Задача отмечена как выполненная. Сотруднику добавлено {hours} часов.")
        else:
            messagebox.showinfo("Выполнено", "Задача отмечена как выполненная.")
        
        self.load_data()
        self.app.projects_tab.load_data()
        self.app.employees_tab.load_data()
    
    def export_to_csv(self):
        """Экспорт задач в CSV"""
        tasks = self.db_manager.get_all_tasks()
        data = []
        for task in tasks:
            emp_name = task.assigned_employee.name if task.assigned_employee else "Не назначен"
            project_title = self.db_manager.get_project_title(task.project_id)
            
            data.append({
                'ID': task.id,
                'Название': task.title,
                'Описание': task.description,
                'Статус': task.status,
                'Требуется часов': task.hours_required,
                'Сотрудник': emp_name,
                'Проект': project_title
            })
        
        df = pd.DataFrame(data)
        filename = export_to_csv(df, "tasks")
        messagebox.showinfo("Экспорт", f"Данные экспортированы в {filename}")