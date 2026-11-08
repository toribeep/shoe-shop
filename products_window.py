# products_window.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ProductsWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.db = app.db
        self.current_user = app.current_user
        self.app.products_window = self
        
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        # константы для фиксированных размеров
        self.IMAGE_WIDTH = 120  
        self.IMAGE_HEIGHT = 120  
        
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        # jчищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.configure(bg='#FFFFFF')
        self.root.title(f"ООО «Обувь» - Главная ({self.current_user.role})")
        
        # панель с логотипом и информацией о пользователе
        self.create_header()
        
        # панель с поиском, фильтрами и кнопками управления
        self.create_controls_panel()
        
        # основной контейнер для товаров 
        self.main_container = tk.Frame(self.root, bg='#FFFFFF')
        self.main_container.pack(fill='both', expand=True, padx=10, pady=5)
    
    def create_header(self):
        header_frame = tk.Frame(self.root, bg='#7FFF00', height=60)
        header_frame.pack(fill='x', padx=5, pady=2)
        header_frame.pack_propagate(False)
        
        left_frame = tk.Frame(header_frame, bg='#7FFF00')
        left_frame.pack(side='left', padx=10)
        
        try:
            logo_path = "resources/Icon.png"
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((40, 40), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = tk.Label(
                    left_frame,
                    image=logo_photo,
                    bg='#7FFF00'
                )
                logo_label.image = logo_photo
                logo_label.pack(side='left', padx=5)
        except Exception as e:
            print(f"Error loading logo: {e}")

        company_label = tk.Label(
            left_frame,
            text='ООО "Обувь"',
            font=("Times New Roman", 16, "bold"),
            bg='#7FFF00'
        )
        company_label.pack(side='left', padx=5, pady=6)
        
        right_frame = tk.Frame(header_frame, bg='#7FFF00')
        right_frame.pack(side='right', padx=10)
        
        user_info = tk.Label(
            right_frame,
            text=f"Пользователь: {self.current_user.full_name}",
            font=("Times New Roman", 10),
            bg='#7FFF00'
        )
        user_info.pack(side='left', padx=5, pady=6)

        logout_btn = tk.Button(
            right_frame,
            text="Выйти",
            font=("Times New Roman", 14),
            bg='#00FA9A',
            command=self.app.logout
        )
        logout_btn.pack(side='left', padx=2, pady=6)
    
    def create_controls_panel(self):
        controls_frame = tk.Frame(self.root, bg='#FFFFFF')
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        if self.current_user.role in ["Менеджер", "Администратор"]:

            filters_frame = tk.Frame(controls_frame, bg='#FFFFFF')
            filters_frame.pack(side='left', fill='x', expand=True)

            tk.Label(
                filters_frame, 
                text="Поиск:", 
                font=("Times New Roman", 10), 
                bg='#FFFFFF'
            ).grid(row=0, column=0, sticky='w', padx=2)
            
            self.search_entry = tk.Entry(
                filters_frame, 
                font=("Times New Roman", 10), 
                width=20
            )
            self.search_entry.grid(row=0, column=1, padx=2)
            self.search_entry.bind('<KeyRelease>', self.on_search_change)

            tk.Label(
                filters_frame, 
                text="Поставщик:", 
                font=("Times New Roman", 10), 
                bg='#FFFFFF'
            ).grid(row=0, column=2, sticky='w', padx=10)
            
            self.supplier_var = tk.StringVar()
            self.supplier_combo = ttk.Combobox(
                filters_frame, 
                textvariable=self.supplier_var,
                font=("Times New Roman", 10), 
                width=12,
                state="readonly"
            )
            self.supplier_combo.grid(row=0, column=3, padx=2)
            self.supplier_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

            tk.Label(
                filters_frame, 
                text="Сортировка:", 
                font=("Times New Roman", 10), 
                bg='#FFFFFF'
            ).grid(row=0, column=4, sticky='w', padx=10)
            
            self.sort_var = tk.StringVar()
            sort_combo = ttk.Combobox(
                filters_frame, 
                textvariable=self.sort_var,
                values=["По умолчанию", "По возрастанию", "По убыванию"],
                font=("Times New Roman", 10), 
                width=12, 
                state="readonly"
            )
            sort_combo.grid(row=0, column=5, padx=2)
            sort_combo.bind('<<ComboboxSelected>>', self.on_sort_change)
 
        buttons_frame = tk.Frame(controls_frame, bg='#FFFFFF')
        buttons_frame.pack(side='right', padx=(20, 0))

        if self.current_user.role in ["Менеджер", "Администратор"]:
            orders_btn = tk.Button(
                buttons_frame,
                text="📋 Заказы",
                font=("Times New Roman", 11),
                bg='#00FA9A',
                command=self.show_orders
            )
            orders_btn.pack(side='left', padx=2)
        
        if self.current_user.role == "Администратор":
            self.add_btn = tk.Button(
                buttons_frame,
                text="➕ Добавить товар",
                font=("Times New Roman", 11),
                bg='#00FA9A',
                command=self.add_product
            )
            self.add_btn.pack(side='left', padx=2)
    
    def load_products(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
        # создание прокрутки
        self.canvas = tk.Canvas(self.main_container, bg='#FFFFFF', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        self.cards_container = tk.Frame(self.canvas, bg='#FFFFFF')
        
        # привязка прокрутки
        self.cards_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Создаем окно в Canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.cards_container, 
            anchor="nw",
            width=self.canvas.winfo_reqwidth()  # занимаем всю ширину Canvas
        )
        
        # настраиваем прокрутку
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # загрузка товаров из базы
        if self.current_user.role in ["Менеджер", "Администратор"]:
            search_text = self.search_entry.get() if hasattr(self, 'search_entry') else ""
            supplier_filter = self.supplier_var.get() if hasattr(self, 'supplier_var') else ""
            sort_by = self.sort_var.get() if hasattr(self, 'sort_var') else ""
            
            # преобразуем сортировку
            sort_mapping = {
                "По возрастанию": "quantity_asc",
                "По убыванию": "quantity_desc"
            }
            sort_param = sort_mapping.get(sort_by, "")
            
            self.products = self.db.get_products_with_filters(search_text, supplier_filter, sort_param)
        else:
            # гость видит все без фильтров
            self.products = self.db.get_all_products()
        
        # обновление фильтра поставщиков
        if hasattr(self, 'supplier_combo'):
            all_products_for_suppliers = self.db.get_all_products()
            all_suppliers = list(set([p.supplier for p in all_products_for_suppliers]))
            all_suppliers.sort()
            all_suppliers.insert(0, "Все поставщики")
            
            current_selection = self.supplier_var.get()
            self.supplier_combo['values'] = all_suppliers
            
            if current_selection in all_suppliers:
                self.supplier_combo.set(current_selection)
            else:
                self.supplier_combo.set("Все поставщики")
        
        # если товаров нет
        if not self.products:
            no_products_label = tk.Label(
                self.cards_container,
                text="Товары не найдены",
                font=("Times New Roman", 14),
                bg='#FFFFFF'
            )
            no_products_label.pack(pady=50)
        else:
            # отображение товаров
            for product in self.products:
                self.create_product_card(product)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind('<Configure>', self.on_canvas_configure)
    
    def on_canvas_configure(self, event):
        """При изменении размера Canvas обновляем ширину контейнера"""
        if hasattr(self, 'cards_container'):
            # устанавливаем ширину контейнера равной ширину Canvas
            self.canvas.itemconfig(self.canvas_window, width=event.width)
    # обработчик наведения на карточку товара
    def on_card_enter(self, event):
        if self.current_user.role == "Администратор":
            event.widget.config(cursor="hand2")
            # находим родительскую карточку
            widget = event.widget
            while widget and not hasattr(widget, 'is_card_frame'):
                widget = widget.master
            
            if widget and hasattr(widget, 'is_card_frame'):
                widget.config(relief='solid', bd=3)
    # jбработчик ухода мыши с карточки товара
    def on_card_leave(self, event):
        if self.current_user.role == "Администратор":
            event.widget.config(cursor="")
            # yаходим родительскую карточку
            widget = event.widget
            while widget and not hasattr(widget, 'is_card_frame'):
                widget = widget.master
            
            if widget and hasattr(widget, 'is_card_frame'):
                widget.config(relief='ridge', bd=2)
    
    def create_product_card(self, product):
        bg_color = '#FFFFFF'
        if product.discount > 15:
            bg_color = '#2E8B57'
        elif product.quantity == 0:
            bg_color = '#ADD8E6'
        
        card_frame = tk.Frame(
            self.cards_container, 
            bg=bg_color,
            relief='ridge', 
            bd=2,
        )
        card_frame.pack(fill='x', padx=5, pady=3, ipadx=5, ipady=5)
        card_frame.is_card_frame = True
        
        # добавление обработчика клика
        if self.current_user.role == "Администратор":
            card_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            card_frame.bind("<Enter>", self.on_card_enter)
            card_frame.bind("<Leave>", self.on_card_leave)
        
        # внутренний контейнер с grid
        inner_container = tk.Frame(card_frame, bg=bg_color)
        inner_container.pack(fill='x', expand=True, padx=10, pady=5)
        
        inner_container.columnconfigure(0, weight=0, minsize=self.IMAGE_WIDTH)    # контейнер для изображения
        inner_container.columnconfigure(1, weight=1)    # контейнер для информации
        inner_container.columnconfigure(2, weight=0, minsize=150)    # контейнер для скидки
        
        
        image_frame = tk.Frame(
            inner_container, 
            bg=bg_color,
            width=self.IMAGE_WIDTH,
            height=self.IMAGE_HEIGHT
        )
        image_frame.grid(row=0, column=0, sticky='nw', padx=5, pady=5)
        image_frame.grid_propagate(False)  
        
        try:
            img_path = None
            if product.photo and os.path.exists(f"resources/{product.photo}"):
                img_path = f"resources/{product.photo}"
            elif os.path.exists("resources/picture.png"):
                img_path = "resources/picture.png"
            
            if img_path:
                img = Image.open(img_path)
                img = img.resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # создаем лейбл
                img_label = tk.Label(
                    image_frame, 
                    image=photo, 
                    bg=bg_color,
                    width=self.IMAGE_WIDTH,
                    height=self.IMAGE_HEIGHT
                )
                img_label.image = photo
                img_label.place(relx=0.5, rely=0.5, anchor='center')  # центрируем изображение
                
                if self.current_user.role == "Администратор":
                    img_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                    img_label.bind("<Enter>", self.on_card_enter)
                    img_label.bind("<Leave>", self.on_card_leave)
            else:
                no_image_label = tk.Label(
                    image_frame, 
                    text="📷\nНет фото", 
                    font=("Times New Roman", 9),
                    bg=bg_color,
                    justify='center',
                    width=int(self.IMAGE_WIDTH/8),  
                    height=int(self.IMAGE_HEIGHT/20)  
                )
                no_image_label.place(relx=0.5, rely=0.5, anchor='center')
                
                if self.current_user.role == "Администратор":
                    no_image_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                    no_image_label.bind("<Enter>", self.on_card_enter)
                    no_image_label.bind("<Leave>", self.on_card_leave)
                    
        except Exception as e:
            print(f"Error loading image: {e}")
            error_label = tk.Label(
                image_frame, 
                text="📷\nОшибка", 
                font=("Times New Roman", 8),
                bg=bg_color,
                justify='center',
                width=int(self.IMAGE_WIDTH/8),
                height=int(self.IMAGE_HEIGHT/20)
            )
            error_label.place(relx=0.5, rely=0.5, anchor='center')
            
            if self.current_user.role == "Администратор":
                error_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                error_label.bind("<Enter>", self.on_card_enter)
                error_label.bind("<Leave>", self.on_card_leave)
        
        # информация о товаре 
        info_frame = tk.Frame(inner_container, bg=bg_color)
        info_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=5)

        title_label = tk.Label(
            info_frame,
            text=f"{product.category} / {product.name}",
            font=("Times New Roman", 12, "bold"),
            bg=bg_color,
            anchor='w'
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        if self.current_user.role == "Администратор":
            title_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            title_label.bind("<Enter>", self.on_card_enter)
            title_label.bind("<Leave>", self.on_card_leave)
        
        # фрейм для деталей товара
        details_frame = tk.Frame(info_frame, bg=bg_color)
        details_frame.pack(fill='x', expand=True, anchor='w')
        
        if product.description:
            desc_text = product.description
            if len(desc_text) > 120:
                desc_text = desc_text[:117] + "..."
            
            desc_label = tk.Label(
                details_frame,
                text=f"Описание товара: {desc_text}",
                font=("Times New Roman", 10),
                bg=bg_color,
                anchor='w',
                justify='left',
                wraplength=550  
            )
            desc_label.pack(anchor='w', pady=2)
            
            if self.current_user.role == "Администратор":
                desc_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                desc_label.bind("<Enter>", self.on_card_enter)
                desc_label.bind("<Leave>", self.on_card_leave)
        
        # производитель
        manufacturer_label = tk.Label(
            details_frame,
            text=f"Производитель: {product.manufacturer}",
            font=("Times New Roman", 10),
            bg=bg_color,
            anchor='w'
        )
        manufacturer_label.pack(anchor='w', pady=2)
        
        if self.current_user.role == "Администратор":
            manufacturer_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            manufacturer_label.bind("<Enter>", self.on_card_enter)
            manufacturer_label.bind("<Leave>", self.on_card_leave)
        
        # поставщик
        supplier_label = tk.Label(
            details_frame,
            text=f"Поставщик: {product.supplier}",
            font=("Times New Roman", 10),
            bg=bg_color,
            anchor='w'
        )
        supplier_label.pack(anchor='w', pady=2)
        
        if self.current_user.role == "Администратор":
            supplier_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            supplier_label.bind("<Enter>", self.on_card_enter)
            supplier_label.bind("<Leave>", self.on_card_leave)
        
        # цена со скидкой 
        price_frame = tk.Frame(details_frame, bg=bg_color)
        price_frame.pack(anchor='w', pady=2)
        
        if self.current_user.role == "Администратор":
            price_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            price_frame.bind("<Enter>", self.on_card_enter)
            price_frame.bind("<Leave>", self.on_card_leave)
        
        price_label_text = tk.Label(
            price_frame,
            text="Цена: ",
            font=("Times New Roman", 10),
            bg=bg_color,
            anchor='w'
        )
        price_label_text.pack(side='left')
        
        if self.current_user.role == "Администратор":
            price_label_text.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            price_label_text.bind("<Enter>", self.on_card_enter)
            price_label_text.bind("<Leave>", self.on_card_leave)
        
        if product.discount > 0:
            # вычисление новой цены
            new_price = product.price * (1 - product.discount / 100)
            
            # старая цена
            old_price_label = tk.Label(
                price_frame,
                text=f"{product.price:.2f}₽",
                font=("Times New Roman", 10, "overstrike"),
                bg=bg_color,
                fg='red',
                anchor='w'
            )
            old_price_label.pack(side='left')
            
            arrow_label = tk.Label(
                price_frame,
                text=" → ",
                font=("Times New Roman", 10),
                bg=bg_color,
                anchor='w'
            )
            arrow_label.pack(side='left')
            
            # новая цена
            new_price_label = tk.Label(
                price_frame,
                text=f"{new_price:.2f}₽",
                font=("Times New Roman", 10, "bold"),
                bg=bg_color,
                fg='black',
                anchor='w'
            )
            new_price_label.pack(side='left')
            
            if self.current_user.role == "Администратор":
                old_price_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                old_price_label.bind("<Enter>", self.on_card_enter)
                old_price_label.bind("<Leave>", self.on_card_leave)
                arrow_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                arrow_label.bind("<Enter>", self.on_card_enter)
                arrow_label.bind("<Leave>", self.on_card_leave)
                new_price_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                new_price_label.bind("<Enter>", self.on_card_enter)
                new_price_label.bind("<Leave>", self.on_card_leave)
        else:
            # если скидки нет, показываем обычную цену
            price_label_value = tk.Label(
                price_frame,
                text=f"{product.price:.2f}₽",
                font=("Times New Roman", 10),
                bg=bg_color,
                anchor='w'
            )
            price_label_value.pack(side='left')
            
            if self.current_user.role == "Администратор":
                price_label_value.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                price_label_value.bind("<Enter>", self.on_card_enter)
                price_label_value.bind("<Leave>", self.on_card_leave)
        
        # единица измерения
        unit_label = tk.Label(
            details_frame,
            text=f"Единица измерения: {product.unit}",
            font=("Times New Roman", 10),
            bg=bg_color,
            anchor='w'
        )
        unit_label.pack(anchor='w', pady=2)
        
        if self.current_user.role == "Администратор":
            unit_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            unit_label.bind("<Enter>", self.on_card_enter)
            unit_label.bind("<Leave>", self.on_card_leave)
        
        # количество на складе
        quantity_color = 'red' if product.quantity == 0 else 'black'
        quantity_text = f"НЕТ В НАЛИЧИИ" if product.quantity == 0 else f"{product.quantity}"
        
        quantity_label = tk.Label(
            details_frame,
            text=f"Количество на складе: {quantity_text}",
            font=("Times New Roman", 10, "bold" if product.quantity == 0 else "normal"),
            bg=bg_color,
            fg=quantity_color,
            anchor='w'
        )
        quantity_label.pack(anchor='w', pady=2)
        
        if self.current_user.role == "Администратор":
            quantity_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            quantity_label.bind("<Enter>", self.on_card_enter)
            quantity_label.bind("<Leave>", self.on_card_leave)
        
        # блок скидки
        discount_frame = tk.Frame(inner_container, bg=bg_color)
        discount_frame.grid(row=0, column=2, sticky='ns', padx=5, pady=5)
        
        if self.current_user.role == "Администратор":
            discount_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            discount_frame.bind("<Enter>", self.on_card_enter)
            discount_frame.bind("<Leave>", self.on_card_leave)
        
        # центрируем содержимое
        discount_content = tk.Frame(discount_frame, bg=bg_color)
        discount_content.pack(expand=True, fill='both')
        
        if product.discount > 0:
            discount_title = tk.Label(
                discount_content,
                text="Действующая скидка",
                font=("Times New Roman", 11, "bold"),
                bg=bg_color,
                fg="#000000"
            )
            discount_title.pack(pady=(10, 0))
            
            discount_percent = tk.Label(
                discount_content,
                text=f"{product.discount}%",
                font=("Times New Roman", 22, "bold"),
                bg=bg_color,
                fg="#000000"
            )
            discount_percent.pack(pady=(5, 10))
            
            if self.current_user.role == "Администратор":
                discount_title.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                discount_title.bind("<Enter>", self.on_card_enter)
                discount_title.bind("<Leave>", self.on_card_leave)
                discount_percent.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                discount_percent.bind("<Enter>", self.on_card_enter)
                discount_percent.bind("<Leave>", self.on_card_leave)
        else:
            # если скидки нет
            no_discount_label = tk.Label(
                discount_content,
                text="Нет скидки",
                font=("Times New Roman", 12),
                bg=bg_color,
                fg='gray'
            )
            no_discount_label.pack(expand=True)
            
            if self.current_user.role == "Администратор":
                no_discount_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                no_discount_label.bind("<Enter>", self.on_card_enter)
                no_discount_label.bind("<Leave>", self.on_card_leave)
    
    def on_search_change(self, event=None):
        self.load_products()
    
    def on_filter_change(self, event=None):
        self.load_products()
    
    def on_sort_change(self, event=None):
        self.load_products()
    # редактирование по клику
    def edit_product(self, product):
        from product_edit_window import ProductEditWindow
        
        # создание окно редактирования
        edit_window = ProductEditWindow(self.root, self.app, product)
        
        self.root.wait_window(edit_window.window)
        # после закрытия окна обновляем список товаров
        self.refresh_products()
    # добавление товара по кнопке
    def add_product(self):
        from product_create_window import ProductCreateWindow
        
        # создание окна создания
        create_window = ProductCreateWindow(self.root, self.app)
        
        self.root.wait_window(create_window.window)
        
        self.refresh_products()
    # обновление списка товаров
    def refresh_products(self):
        self.load_products()
    # переход к окну заказов
    def show_orders(self):
        from orders_window import OrdersWindow
        OrdersWindow(self.root, self.app)