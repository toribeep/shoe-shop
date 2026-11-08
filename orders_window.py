# orders_window.py
import tkinter as tk
from tkinter import ttk, messagebox

class OrdersWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.db = app.db
        self.app.orders_window = self
        self.setup_ui()
        self.load_orders()
    
    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.configure(bg='white')
        self.root.title("Список заказов")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        header_frame = tk.Frame(self.root, bg='#7FFF00', height=50)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📋 Список заказов", 
                font=("Times New Roman", 16, "bold"), bg='#7FFF00'
        ).pack(side='left', padx=20, pady=10)
       
        back_btn = tk.Button(header_frame, text="← Назад к товарам", font=("Times New Roman", 10),
                           bg='#00FA9A', command=self.go_back_to_products)
        back_btn.pack(side='right', padx=20, pady=10)
        
        # основной контейнер для заказов
        self.main_container = tk.Frame(self.root, bg='#FFFFFF')
        self.main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        if self.app.current_user.role == "Администратор":
            add_btn = tk.Button(self.root, text="➕ Добавить заказ", font=("Times New Roman", 12),
                              bg='#00FA9A', command=self.add_order)
            add_btn.pack(pady=10)
    
    def load_orders(self):
        # очищение предыдущих заказов
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # создание Canvas для прокрутки
        self.canvas = tk.Canvas(self.main_container, bg='#FFFFFF', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        # контейнер для карточек заказов
        self.cards_container = tk.Frame(self.canvas, bg='#FFFFFF')
        
        # привязка прокрутки
        self.cards_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # создание окна в сanvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.cards_container, 
            anchor="nw",
            width=self.canvas.winfo_reqwidth()
        )
        
        # настраиваем прокрутку
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # загрузка заказов из базы
        orders = self.db.get_all_orders()
        
        if not orders:
            no_orders_label = tk.Label(
                self.cards_container,
                text="Заказы не найдены",
                font=("Times New Roman", 14),
                bg='#FFFFFF'
            )
            no_orders_label.pack(pady=50)
        else:
            # отображение заказов
            for order in orders:
                self.create_order_card(order)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind('<Configure>', self.on_canvas_configure)
    
    def on_canvas_configure(self, event):
        if hasattr(self, 'cards_container'):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def create_order_card(self, order):
        status_colors = {
            "Новый": "#FFFFFF",
            "В обработке": "#7FFF00",
            "Доставляется": "#7FFF00",
            "Завершен": "#FFFFFF",
            "Отменен": "#00FA9A"
        }
        bg_color = status_colors.get(order.status, "#FFFFFF")
    
        # основной фрейм карточки
        card_frame = tk.Frame(
            self.cards_container, 
            bg=bg_color,
            relief='ridge', 
            bd=2,
        )
        card_frame.pack(fill='x', padx=5, pady=3, ipadx=5, ipady=5)
        card_frame.is_order_card = True
    
    # обработчик двойного клика (только для админа)
        if self.app.current_user.role == "Администратор":
            card_frame.bind("<Double-1>", lambda e, o=order: self.edit_order(o))
    
    # внутренний контейнер с grid
        inner_container = tk.Frame(card_frame, bg=bg_color)
        inner_container.pack(fill='x', expand=True, padx=10, pady=5)
        inner_container.columnconfigure(0, weight=1)    
        inner_container.columnconfigure(1, weight=0, minsize=200)    

        left_frame = tk.Frame(inner_container, bg=bg_color)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    
        order_data = [
            f"Артикул заказа: {order.order_articles}",
            f"Статус заказа: {order.status}",
            f"Адрес пункта выдачи: {order.pickup_address}",
            f"Дата заказа: {order.order_date.strftime('%d.%m.%Y')}"
        ]
    
    # отображение каждый пункт списка
        for i, data in enumerate(order_data):
            data_label = tk.Label(
                left_frame,
                text=data,
                font=("Times New Roman", 11),
                bg=bg_color,
                anchor='w'
            )
            data_label.pack(anchor='w', pady=3)
        
        # Добавляем обработчик двойного клика для ВСЕХ лейблов
            if self.app.current_user.role == "Администратор":
                data_label.bind("<Double-1>", lambda e, o=order: self.edit_order(o))
            # Также добавим обработчик для наведения курсора
                data_label.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
                data_label.bind("<Leave>", lambda e: e.widget.config(cursor=""))
    
    # 2. ПРАВАЯ ЧАСТЬ: ДАТА ДОСТАВКИ
        right_frame = tk.Frame(inner_container, bg=bg_color)
        right_frame.grid(row=0, column=1, sticky='ns', padx=5, pady=5)
    
    # Центрируем содержимое
        delivery_content = tk.Frame(right_frame, bg=bg_color)
        delivery_content.pack(expand=True, fill='both')
    
    # Добавляем обработчик двойного клика для всей правой части
        if self.app.current_user.role == "Администратор":
            right_frame.bind("<Double-1>", lambda e, o=order: self.edit_order(o))
            delivery_content.bind("<Double-1>", lambda e, o=order: self.edit_order(o))
    
    # Заголовок "Дата доставки"
        delivery_title = tk.Label(
            delivery_content,
            text="Дата доставки",
            font=("Times New Roman", 12, "bold"),
            bg=bg_color
        )
        delivery_title.pack(pady=(10, 5))
    
    # Добавляем обработчик для заголовка
        if self.app.current_user.role == "Администратор":
            delivery_title.bind("<Double-1>", lambda e, o=order: self.edit_order(o))
            delivery_title.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
            delivery_title.bind("<Leave>", lambda e: e.widget.config(cursor=""))
    
    # Дата доставки крупным шрифтом
        delivery_date = order.delivery_date.strftime("%d.%m.%Y")
        delivery_date_label = tk.Label(
        delivery_content,
        text=delivery_date,
        font=("Times New Roman", 18, "bold"),
        bg=bg_color
    )
        delivery_date_label.pack(pady=(5, 10))
        
        # Добавляем обработчик для даты доставки
        if self.app.current_user.role == "Администратор":
            delivery_date_label.bind("<Double-1>", lambda e, o=order: self.edit_order(o))
            delivery_date_label.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
            delivery_date_label.bind("<Leave>", lambda e: e.widget.config(cursor=""))
    
    def edit_order(self, order):
        """Редактирование заказа по двойному клику"""
        try:
            from order_edit_window import OrderEditWindow
            # Создаем окно редактирования
            edit_window = OrderEditWindow(self.root, self.app, order)
            
            # Ждем закрытия окна редактирования
            self.root.wait_window(edit_window.window)
            
            # Обновляем список заказов сразу после закрытия окна
            self.refresh_orders()
            
        except ImportError as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть окно редактирования: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    
    def add_order(self):
        """Добавление нового заказа"""
        try:
            from order_create_window import OrderCreateWindow
            # Создаем окно создания
            create_window = OrderCreateWindow(self.root, self.app)
            
            # Ждем закрытия окна создания
            self.root.wait_window(create_window.window)
            
            # Обновляем список заказов сразу после закрытия окна
            self.refresh_orders()
            
        except ImportError as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть окно добавления: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    
    def refresh_orders(self):
        """Обновление списка заказов"""
        self.load_orders()
    
    def go_back_to_products(self):
        """Возврат к окну товаров"""
        try:
            from products_window import ProductsWindow
            ProductsWindow(self.root, self.app)
        except ImportError as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть окно товаров: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")