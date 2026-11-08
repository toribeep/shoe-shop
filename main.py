# main.py
import tkinter as tk
from tkinter import messagebox
from auth_window import AuthWindow  
from database import Database

class ShoeStoreApp:
    def __init__(self):
        try:
            self.db = Database()
            self.current_user = None
            self.current_window = None 
            self.root = tk.Tk()
            self.setup_main_window()
            self.show_auth_window()
        except Exception as e:
            messagebox.showerror("Ошибка инициализации", f"Не удалось запустить приложение: {e}")
            raise
    
    def setup_main_window(self):
        # фиксированный размер окна
        self.root.title("Обувной магазин - ООО «Обувь»")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)  # запрещение изменения размера
        self.root.configure(bg='white')
        
        self.center_window() # по центру
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_auth_window(self):
        try:
            AuthWindow(self.root, self)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть окно авторизации: {e}")
    
    def login_successful(self, user):
        self.current_user = user
        try:
            from products_window import ProductsWindow
            ProductsWindow(self.root, self)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть список товаров: {e}")
            self.show_auth_window()
    
    def logout(self):
        self.current_user = None
        self.show_auth_window()
    
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Приложение завершилось с ошибкой: {e}")
        finally:
            if hasattr(self, 'db'):
                self.db.close()

if __name__ == "__main__":
    app = ShoeStoreApp()
    app.run()