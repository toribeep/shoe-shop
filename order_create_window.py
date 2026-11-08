# order_create_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import Order

class OrderCreateWindow:
    def __init__(self, parent, app):
        """
        Окно создания нового заказа
        """
        self.parent = parent
        self.app = app
        self.db = app.db
        self.pickup_points = []  # список пунктов выдачи
        
        # создание окна
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление нового заказа")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        self.window.configure(bg='white')
        self.window.transient(parent)
        self.window.grab_set()
        self.center_window()
        
        # переменные для хранения данных формы
        self.order_number_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.pickup_address_id_var = tk.StringVar() 
        self.client_name_var = tk.StringVar()
        self.order_date_var = tk.StringVar()
        self.delivery_date_var = tk.StringVar()
        self.pickup_code_var = tk.StringVar()
        self.order_articles_var = tk.StringVar()
        
        self.setup_ui()
        self.load_initial_data()
        
        # обработчик закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
    # центрирование окна
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
    # загрузка пунктов выдачи из бд
    def load_pickup_points(self):
        try:
            self.pickup_points = self.db.get_all_pickup_points()
        except Exception as e:
            print(f"Error loading pickup points: {e}")
            self.pickup_points = []
    
    def setup_ui(self):
        """Создание интерфейса окна"""
        self.window.configure(bg='white')
        
        title_label = tk.Label(
            self.window,
            text="Добавление нового заказа",
            font=("Times New Roman", 16, "bold"),
            bg='white'
        )
        title_label.pack(pady=10)
        
        main_container = tk.Frame(self.window, bg='white')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        fields_frame = tk.Frame(main_container, bg='white')
        fields_frame.pack(fill='both', expand=True)
        
        # настройка grid
        for i in range(2):
            fields_frame.columnconfigure(i, weight=1)
        
        row = 0
        
        articles_frame = tk.Frame(fields_frame, bg='white')
        articles_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        tk.Label(articles_frame, text="Артикул заказа* (формат: артикул1, количество1, артикул2, количество2, ...):", 
                font=("Times New Roman", 12), bg='white').pack(anchor='w', pady=2)
        
        # создание Text виджет для многострочного ввода
        articles_text = tk.Text(articles_frame, font=("Times New Roman", 10), 
                               width=70, height=3)
        articles_text.pack(fill='x', pady=2)
        def update_articles_var():
            self.order_articles_var.set(articles_text.get("1.0", "end-1c").strip())
        
        articles_text.bind("<KeyRelease>", lambda e: update_articles_var())
        
        self.articles_text_widget = articles_text
        
        help_label = tk.Label(articles_frame, 
                             text="Пример: А112Т4, 2, F635R4, 2",
                             font=("Times New Roman", 9, "italic"),
                             bg='white', fg='gray')
        help_label.pack(anchor='w', pady=(2, 0))
        
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
        
        address_id_entry = tk.Entry(address_frame, textvariable=self.pickup_address_id_var,
                                   font=("Times New Roman", 10), width=30)
        address_id_entry.pack(fill='x', pady=2)
        
        row += 1
       
        client_frame = tk.Frame(fields_frame, bg='white')
        client_frame.grid(row=row, column=0, sticky='ew', padx=5, pady=10)
        
        tk.Label(client_frame, text="ФИО авторизированного клиента*:", 
                font=("Times New Roman", 12), bg='white').pack(anchor='w', pady=2)
        
        client_entry = tk.Entry(client_frame, textvariable=self.client_name_var,
                               font=("Times New Roman", 10), width=30)
        client_entry.pack(fill='x', pady=2)
        
        code_frame = tk.Frame(fields_frame, bg='white')
        code_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=10)
        
        tk.Label(code_frame, text="Код для получения*:", 
                font=("Times New Roman", 12), bg='white').pack(anchor='w', pady=2)
        
        code_entry = tk.Entry(code_frame, textvariable=self.pickup_code_var,
                             font=("Times New Roman", 10), width=30)
        code_entry.pack(fill='x', pady=2)
        
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
        
        # кнопки управления
        buttons_frame = tk.Frame(self.window, bg='white')
        buttons_frame.pack(fill='x', pady=15, padx=20)
        
        # настройка grid для кнопок 
        buttons_frame.columnconfigure(0, weight=1)  
        buttons_frame.columnconfigure(1, weight=1)  
        buttons_frame.columnconfigure(2, weight=1)  
    
        cancel_btn = tk.Button(
            buttons_frame,
            text="Отмена",
            font=("Times New Roman", 12),
            bg="#00FA9A",
            fg='black',
            width=15,
            height=2,
            command=self.cancel
        )
        cancel_btn.grid(row=0, column=0, padx=5)
        
        # выравнивание для красоты
        tk.Frame(buttons_frame, bg='white', width=15, height=2).grid(row=0, column=1, padx=5)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Создать заказ",
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
    
    #Загрузка начальных данных для нового заказа
    def load_initial_data(self):
        # генерация номера заказа
        next_number = self.db.get_max_order_number() + 1
        self.order_number_var.set(str(next_number))
        # установка текущей даты как дату заказа
        self.order_date_var.set(datetime.now().strftime("%d.%m.%Y"))
        self.status_var.set("Новый")
        self.load_pickup_points()
    # парсинг даты
    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            raise ValueError(f"Некорректный формат даты: {date_str}. Ожидается ДД.ММ.ГГГГ")
    # парсинг артикулов товаров 
    def parse_articles(self, articles_text):
        parts = [part.strip() for part in articles_text.split(',')]
        
        if len(parts) == 0:
            raise ValueError("Строка артикулов пуста")
        
        if len(parts) % 2 != 0:
            raise ValueError("Нечетное количество элементов. Ожидается: артикул, количество, артикул, количество...")
        
        result = []
        for i in range(0, len(parts), 2):
            article = parts[i]
            quantity_str = parts[i + 1]
            # проверка на пустые значения
            if not article:
                raise ValueError(f"Пустой артикул на позиции {i+1}")
            if not quantity_str:
                raise ValueError(f"Пустое количество для артикула '{article}'")
            # проверка количества
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    raise ValueError(f"Количество должно быть положительным для артикула '{article}'")
            except ValueError:
                raise ValueError(f"Некорректное количество '{quantity_str}' для артикула '{article}'")
            # проверка существования артикула в базе
            product = self.db.get_product_by_article(article)
            if not product:
                raise ValueError(f"Артикул '{article}' не найден в базе товаров")
            
            result.append((article, quantity))
        
        return result
    
    # валидация полей
    def validate_fields(self):
        errors = []
        if not self.order_articles_var.get().strip():
            errors.append("Артикул заказа обязателен для заполнения")
        else:
            try:
                self.parse_articles(self.order_articles_var.get().strip())
            except ValueError as e:
                errors.append(f"Ошибка в артикулах заказа: {e}")
        if not self.status_var.get().strip():
            errors.append("Статус заказа обязателен для выбора")
        pickup_id_str = self.pickup_address_id_var.get().strip()
        if not pickup_id_str:
            errors.append("ID пункта выдачи обязателен для заполнения")
        else:
            try:
                pickup_id = int(pickup_id_str)
                # проверка существувет ли такой пункт
                point_exists = False
                for point in self.pickup_points:
                    if point.id == pickup_id:
                        point_exists = True
                        break
                
                if not point_exists:
                    errors.append(f"Пункт выдачи с ID {pickup_id} не найден. Доступные ID: 1-36")
            except ValueError:
                errors.append("ID пункта выдачи должен быть числом")

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
                
                # Проверяем, что дата выдачи не раньше даты заказа
                if 'order_date' in locals():
                    if delivery_date < order_date:
                        errors.append("Дата выдачи не может быть раньше даты заказа")
            except ValueError as e:
                errors.append(str(e))
        
        return errors
    # сохранение заказа
    def save_order(self):
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Ошибки валидации", "\n".join(errors))
            return
        
        try:
            # получение данных
            order_number = int(self.order_number_var.get().strip())
            status = self.status_var.get().strip()
            pickup_id = int(self.pickup_address_id_var.get().strip())
            client_name = self.client_name_var.get().strip()
            order_date = self.parse_date(self.order_date_var.get().strip())
            delivery_date = self.parse_date(self.delivery_date_var.get().strip())
            pickup_code = self.pickup_code_var.get().strip()
            order_articles = self.order_articles_var.get().strip()
            
            # создание объекта заказа
            order = Order(
                order_number=order_number,
                order_articles=order_articles,
                order_date=order_date,
                delivery_date=delivery_date,
                pickup_address=pickup_id,  
                client_name=client_name,
                pickup_code=pickup_code,
                status=status
            )
            
            self.db.add_order(order)
            messagebox.showinfo("Успех", f"Заказ №{order_number} успешно создан!")
            
            self.window.destroy()
            
            self.refresh_parent_orders()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать заказ: {e}")
            print(f"Create order error: {e}")
    # обновление заказов
    def refresh_parent_orders(self):
        
        if hasattr(self.app, 'orders_window'):
            self.app.orders_window.refresh_orders()
        elif hasattr(self.app, 'refresh_orders'):
            self.app.refresh_orders()
    
    def cancel(self):
        self.window.destroy()