"""
Вкладка для работы с проектами
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from models import Project
from utils import export_to_csv

class ProjectsTab:
    def __init__(self, parent, db_manager, app):
        self.parent = parent
        self.db_manager = db_manager
        self.app = app
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки проектов"""
        # Верхняя панель с кнопками
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Добавить", 
                  command=self.add_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Редактировать", 
                  command=self.edit_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить", 
                  command=self.delete).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV", 
                  command=self.export_to_csv).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить", 
                  command=self.load_data).pack(side='left', padx=5)
        
        # Таблица проектов
        columns = ('ID', 'Название', 'Всего задач', 'Завершено', 'Прогресс', 'Всего часов')
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
        """Загрузка данных проектов"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        projects = self.db_manager.get_all_projects()
        for project in projects:
            project_dict = project.to_dict()
            
            total_hours = sum(task.hours_required for task in project.tasks)
            
            self.tree.insert('', 'end', values=(
                project.id, project.title, 
                project_dict['total_tasks'], project_dict['completed_tasks'],
                project_dict['progress'], f"{total_hours:.1f}"
            ))
    
    def add_dialog(self):
        """Диалог добавления проекта"""
        self.project_dialog("Добавить проект", None)
    
    def edit_dialog(self):
        """Диалог редактирования проекта"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите проект для редактирования")
            return
        
        item = self.tree.item(selection[0])
        project_id = item['values'][0]
        
        projects = self.db_manager.get_all_projects()
        project = next((p for p in projects if p.id == project_id), None)
        
        if project:
            self.project_dialog("Редактировать проект", project)
    
    def project_dialog(self, title, project):
        """Общий диалог для добавления/редактирования проекта"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title(title)
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Название проекта:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        title_var = tk.StringVar(value=project.title if project else "")
        title_entry = ttk.Entry(dialog, textvariable=title_var, width=30)
        title_entry.grid(row=0, column=1, padx=10, pady=10)
        
        def save_project():
            title_val = title_var.get()
            
            if not title_val:
                messagebox.showerror("Ошибка", "Введите название проекта")
                return
            
            if project:
                project.title = title_val
                self.db_manager.update_project(project)
            else:
                new_project = Project(title_val)
                self.db_manager.add_project(new_project)
            
            self.load_data()
            self.app.tasks_tab.load_data()
            dialog.destroy()
            messagebox.showinfo("Успех", "Проект сохранен")
        
        ttk.Button(dialog, text="Сохранить", command=save_project).grid(row=1, column=0, columnspan=2, pady=20)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=2, column=0, columnspan=2)
    
    def delete(self):
        """Удаление проекта"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите проект для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный проект и все его задачи?"):
            item = self.tree.item(selection[0])
            project_id = item['values'][0]
            self.db_manager.delete_project(project_id)
            self.load_data()
            self.app.tasks_tab.load_data()
            self.app.employees_tab.load_data()
            messagebox.showinfo("Удалено", "Проект и все его задачи удалены")
    
    def export_to_csv(self):
        """Экспорт проектов в CSV"""
        projects = self.db_manager.get_all_projects()
        data = []
        for project in projects:
            project_dict = project.to_dict()
            
            total_hours = sum(task.hours_required for task in project.tasks)
            completed_hours = sum(task.hours_required for task in project.tasks if task.status == "Завершено")
            
            data.append({
                'ID': project.id,
                'Название': project.title,
                'Всего задач': project_dict['total_tasks'],
                'Завершено задач': project_dict['completed_tasks'],
                'Прогресс': project_dict['progress'],
                'Всего часов': total_hours,
                'Выполнено часов': completed_hours
            })
        
        df = pd.DataFrame(data)
        filename = export_to_csv(df, "projects")
        messagebox.showinfo("Экспорт", f"Данные экспортированы в {filename}")