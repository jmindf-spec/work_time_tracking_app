import tkinter as tk

# Используем абсолютный импорт
from gui.main_window import TimeTrackingApp

def main():
    """Основная функция запуска приложения"""
    root = tk.Tk()
    app = TimeTrackingApp(root)
    
    # Центрируем окно на экране
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()