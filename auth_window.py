# auth_window.py
import tkinter as tk
from tkinter import messagebox
from models import User

class AuthWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.db = app.db
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
       
        self.root.configure(bg='white')
        
        title_label = tk.Label(
            self.root, 
            text="Авторизация", 
            font=("Times New Roman", 20, "bold"),
            bg='white'
        )
        title_label.pack(pady=100) 
        
        # фрейм для полей ввода
        input_frame = tk.Frame(self.root, bg='white')
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Логин:", font=("Times New Roman", 12), 
                bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.login_entry = tk.Entry(input_frame, font=("Times New Roman", 12), width=30)
        self.login_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="Пароль:", font=("Times New Roman", 12), 
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.password_entry = tk.Entry(input_frame, font=("Times New Roman", 12), 
                                      width=30, show='*')
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)
        
        login_btn = tk.Button(
            self.root, 
            text="Войти", 
            font=("Times New Roman", 12),
            bg='#00FA9A',
            fg='black',
            width=15,
            command=self.login
        )
        login_btn.pack(pady=10)
        
        guest_btn = tk.Button(
            self.root, 
            text="Войти как гость", 
            font=("Times New Roman", 12),
            bg='#7FFF00',
            fg='black',
            width=15,
            command=self.guest_login
        )
        guest_btn.pack(pady=5)
        
    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
        
        user = self.db.get_user_by_credentials(login, password)
        if user:
            self.app.login_successful(user)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    
    def guest_login(self):
        guest_user = User(
            id=0,
            role="Гость",
            full_name="Гость",
            login="guest",
            password=""
        )
        self.app.login_successful(guest_user)