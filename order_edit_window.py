# order_edit_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import Order

class OrderEditWindow:
    def __init__(self, parent, app, order):
        """
        Окно редактирования существующего заказа
        order - редактируемый заказ
        """
        self.parent = parent
        self.app = app
        self.db = app.db
        self.order = order
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Редактирование заказа")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        self.window.configure(bg='white')
        self.window.transient(parent)
        self.window.grab_set()
        
        self.center_window()
        
        self.order_number_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.pickup_address_var = tk.StringVar()
        self.client_name_var = tk.StringVar()
        self.order_date_var = tk.StringVar()
        self.delivery_date_var = tk.StringVar()
        self.pickup_code_var = tk.StringVar()
        self.order_articles_var = tk.StringVar()
        
        self.setup_ui()
        self.load_order_data()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        if self.parent:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)
        else:
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
        
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_window_close(self):
        self.window.destroy()

    # создание интерфейса 
    def setup_ui(self):
        self.window.configure(bg='white')
        
        title_label = tk.Label(
            self.window,
            text="Редактирование заказа",
            font=("Times New Roman", 16, "bold"),
            bg='white'
        )
        title_label.pack(pady=10)

        # основной контейнер
        main_container = tk.Frame(self.window, bg='white')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # фрейм для полей ввода
        fields_frame = tk.Frame(main_container, bg='white')
        fields_frame.pack(fill='both', expand=True)

        # настраиваем grid
        for i in range(2):
            fields_frame.columnconfigure(i, weight=1)
        row = 0
        
        articles_frame = tk.Frame(fields_frame, bg='white')
        articles_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        tk.Label(articles_frame, text="Артикул заказа (не редактируемое поле):", 
                font=("Times New Roman", 12), bg='white').pack(anchor='w', pady=2)
        
        # создаем Text виджет для многострочности
        articles_text = tk.Text(articles_frame, font=("Times New Roman", 10), 
                               width=70, height=2, bg='#f5f5f5')
        articles_text.pack(fill='x', pady=2)
        
        # поле только для чтения
        articles_text.config(state='disabled')
        self.articles_text_widget = articles_text
       
        row += 1
        
        status_frame = tk.Frame(fields_frame, bg='white')
        status_frame.grid(row=row, column=0, sticky='ew', padx=5, pady=10)
        
        tk.Label(status_frame, text="Статус заказа*:", 
                font=("Times New Roman", 12), bg='white').pack(anchor='w', pady=2)
        
        status_options = ["Новый", "В обработке", "Доставляется", "Завершен", "Отменен"]
        status_combo = ttk.Combobox(status_frame, textvariable=self.status_var,
                                   values=status_options, font=("Times New Roman", 10),
                                   width=28, state="readonly")
        status_combo.pack(fill='x', pady=2)
        
        address_frame = tk.Frame(fields_frame, bg='white')
        address_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=10)
        
        tk.Label(address_frame, text="Адрес пункта выдачи*:", 
                font=("Times New Roman", 12), bg='white').pack(anchor='w', pady=2)
        
        address_entry = tk.Entry(address_frame, textvariable=self.pickup_address_var,
                                font=("Times New Roman", 10), width=30)
        address_entry.pack(fill='x', pady=2)
        
        row += 1
        
        order_date_frame = tk.Frame(fields_frame, bg='white')
        order_date_frame.grid(row=row, column=0, sticky='ew', padx=5, pady=10)
        
        tk.Label(order_date_frame, text="Дата заказа* (ДД.ММ.ГГГГ):", 
                font=("Times New Roman", 12), bg='white').pack(anchor='w', pady=2)
        
        order_date_entry = tk.Entry(order_date_frame, textvariable=self.order_date_var,
                                   font=("Times New Roman", 10), width=30)
        order_date_entry.pack(fill='x', pady=2)
    
        delivery_date_frame = tk.Frame(fields_frame, bg='white')
        delivery_date_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=10)
        
        tk.Label(delivery_date_frame, text="Дата доставки* (ДД.ММ.ГГГГ):", 
                font=("Times New Roman", 12), bg='white').pack(anchor='w', pady=2)
        
        delivery_date_entry = tk.Entry(delivery_date_frame, textvariable=self.delivery_date_var,
                                      font=("Times New Roman", 10), width=30)
        delivery_date_entry.pack(fill='x', pady=2)
        
        # кнопки
        buttons_frame = tk.Frame(self.window, bg='white')
        buttons_frame.pack(fill='x', pady=15, padx=20)
        
        buttons_frame.columnconfigure(0, weight=1)  
        buttons_frame.columnconfigure(1, weight=1)  
        buttons_frame.columnconfigure(2, weight=1)  
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Отмена",
            font=("Times New Roman", 12),
            bg="#FFFFFF",
            fg='black',
            width=15,
            height=2,
            command=self.cancel
        )
        cancel_btn.grid(row=0, column=0, padx=5)
        
        if self.app.current_user.role == "Администратор":
            delete_btn = tk.Button(
                buttons_frame,
                text="Удалить заказ",
                font=("Times New Roman", 12),
                bg='#00FA9A',  
                fg='black',
                width=15,
                height=2,
                command=self.delete_order
            )
            delete_btn.grid(row=0, column=1, padx=5)
        else:
            # заполнитель для выравнивания
            tk.Frame(buttons_frame, bg='white', width=15, height=2).grid(row=0, column=1, padx=5)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Сохранить изменения",
            font=("Times New Roman", 12, "bold"),
            bg='#7FFF00',
            fg='black',
            width=18,
            height=2,
            command=self.save_order
        )
        save_btn.grid(row=0, column=2, padx=5)
        
        mandatory_label = tk.Label(
            self.window,
            text="* - обязательные для заполнения поля",
            font=("Times New Roman", 10, "italic"),
            bg='white',
            fg='gray'
        )
        mandatory_label.pack(pady=(0, 10))
    # загрузка данных редактируемого заказа
    def load_order_data(self):
        self.order_number_var.set(str(self.order.order_number))
        self.status_var.set(self.order.status)
        self.pickup_address_var.set(self.order.pickup_address)
        self.client_name_var.set(self.order.client_name)
        self.pickup_code_var.set(self.order.pickup_code)
        self.order_date_var.set(self.order.order_date.strftime("%d.%m.%Y"))
        self.delivery_date_var.set(self.order.delivery_date.strftime("%d.%m.%Y"))
        
        if hasattr(self, 'articles_text_widget'):
            self.articles_text_widget.delete("1.0", "end")
            self.articles_text_widget.insert("1.0", self.order.order_articles)
            self.articles_text_widget.config(state='disabled')  
            self.order_articles_var.set(self.order.order_articles)
    # парсинг даты
    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            raise ValueError(f"Некорректный формат даты: {date_str}. Ожидается ДД.ММ.ГГГГ")
    # валидация полей формы
    def validate_fields(self):
        errors = []
        
        if not self.status_var.get().strip():
            errors.append("Статус заказа обязателен для выбора")
        if not self.pickup_address_var.get().strip():
            errors.append("Адрес пункта выдачи обязателен для заполнения")
        if not self.client_name_var.get().strip():
            errors.append("ФИО авторизированного клиента обязательно для заполнения")
        if not self.pickup_code_var.get().strip():
            errors.append("Код для получения обязателен для заполнения")
        if not self.order_date_var.get().strip():
            errors.append("Дата заказа обязательна для заполнения")
        else:
            try:
                order_date = self.parse_date(self.order_date_var.get().strip())
            except ValueError as e:
                errors.append(str(e))
        if not self.delivery_date_var.get().strip():
            errors.append("Дата выдачи обязательна для заполнения")
        else:
            try:
                delivery_date = self.parse_date(self.delivery_date_var.get().strip())
                # проверка что дата выдачи не раньше даты заказа
                if 'order_date' in locals():
                    if delivery_date < order_date:
                        errors.append("Дата выдачи не может быть раньше даты заказа")
            except ValueError as e:
                errors.append(str(e))
        
        return errors
    # сохранение изменений в заказе
    def save_order(self):
        """Сохранение изменений в заказе"""
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Ошибки валидации", "\n".join(errors))
            return
        
        try:
            # получение данных из формы
            order_number = int(self.order_number_var.get().strip())
            status = self.status_var.get().strip()
            pickup_address = self.pickup_address_var.get().strip()
            client_name = self.client_name_var.get().strip()
            order_date = self.parse_date(self.order_date_var.get().strip())
            delivery_date = self.parse_date(self.delivery_date_var.get().strip())
            pickup_code = self.pickup_code_var.get().strip()
            
            # артикулы заказа остаются без изменений (берем из исходного заказа)
            order_articles = self.order.order_articles
            
            # объект заказа с обновлениями
            order = Order(
                order_number=order_number,
                order_articles=order_articles,
                order_date=order_date,
                delivery_date=delivery_date,
                pickup_address=pickup_address,
                client_name=client_name,
                pickup_code=pickup_code,
                status=status
            )
            
            # обновление заказа
            self.db.update_order(order)
            messagebox.showinfo("Успех", f"Заказ №{order_number} успешно обновлен!")
            
            self.window.destroy()
            
            self.refresh_parent_orders()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить заказ: {e}")
            print(f"Update order error: {e}")
    # удаление заказа
    def delete_order(self):
        order_number = self.order.order_number
        
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заказ №{order_number}?\n\n"
            f"Клиент: {self.order.client_name}\n"
            f"Адрес: {self.order.pickup_address}\n"
            f"Статус: {self.order.status}\n\n"
            "Это действие нельзя отменить!"
        )
        
        if not confirm:
            return
        
        try:
            success = self.db.delete_order(order_number)
            
            if success:
                messagebox.showinfo("Успех", f"Заказ №{order_number} успешно удален!")
                
                self.window.destroy()
                
                self.refresh_parent_orders()
            else:
                messagebox.showerror("Ошибка", 
                    f"Не удалось удалить заказ №{order_number}.\n"
                    "Возможно, заказ содержит товары, которые не могут быть удалены."
                )
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении заказа: {e}")
            print(f"Delete order error: {e}")

    def refresh_parent_orders(self):
        if hasattr(self.app, 'orders_window'):
            self.app.orders_window.refresh_orders()
        elif hasattr(self.app, 'refresh_orders'):
            self.app.refresh_orders()

    def cancel(self):
        self.window.destroy()