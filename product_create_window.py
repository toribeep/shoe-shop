# product_create_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil
import re
import uuid
from models import Product
# окно добавления нового товара
class ProductCreateWindow:
    def __init__(self, parent, app):
        
        self.parent = parent
        self.app = app
        self.db = app.db
        self.photo_path = None
        
        # создаем окно
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление нового товара")
        self.window.geometry("1200x650")
        self.window.resizable(False, False)
        self.window.configure(bg='white')
        self.window.transient(parent)
        self.window.grab_set()
        
        # центрируем окно
        self.center_window()
        
        # переменные для хранения данных формы
        self.article_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.manufacturer_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.price_var = tk.StringVar(value=0.0)
        self.unit_var = tk.StringVar(value="шт")
        self.quantity_var = tk.StringVar(value=0)
        self.discount_var = tk.StringVar(value=0.0)
        
        # следующий артикул
        self.calculate_next_article()
        
        self.setup_ui()
        self.load_initial_data()
        
        # обработчик закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)

    # центрирование окна относительно родителя
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

    # обработчик закрытия окна
    def on_window_close(self):
        self.window.destroy()

    # создание интерфейса окна добавления
    def setup_ui(self):
        self.window.configure(bg='white')
        
        # заголовок окна
        title_label = tk.Label(
            self.window,
            text="Добавление нового товара",
            font=("Times New Roman", 16, "bold"),
            bg='white'
        )
        title_label.pack(pady=10)
        
        # основной контейнер
        main_container = tk.Frame(self.window, bg='white')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # фото и основные поля
        top_frame = tk.Frame(main_container, bg='white')
        top_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # фото товара
        left_column = tk.Frame(top_frame, bg='white')
        left_column.pack(side='left', fill='y', padx=(0, 30))
        
        photo_label_frame = tk.LabelFrame(left_column, text="Фото товара (300×200)", 
                                         font=("Times New Roman", 12), bg='white', padx=10, pady=10)
        photo_label_frame.pack()
        
        self.photo_label = tk.Label(photo_label_frame, bg='lightgray', width=40, height=15)
        self.photo_label.pack()
        
        # кнопки для фото
        photo_buttons = tk.Frame(photo_label_frame, bg='white')
        photo_buttons.pack(pady=10)
        
        load_photo_btn = tk.Button(
            photo_buttons,
            text="Загрузить фото",
            font=("Times New Roman", 10),
            bg='#00FA9A',
            width=15,
            command=self.load_photo
        )
        load_photo_btn.pack()
        
        right_column = tk.Frame(top_frame, bg='white')
        right_column.pack(side='left', fill='both', expand=True)
        
        # основные поля в 3 колонки
        fields_row = tk.Frame(right_column, bg='white')
        fields_row.pack(fill='x', pady=(0, 10))
        
        # Создаем 3 колонки
        for i in range(3):
            fields_row.columnconfigure(i, weight=1)
        
        # наименование товара
        name_frame = tk.Frame(fields_row, bg='white')
        name_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        tk.Label(name_frame, text="Наименование товара*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        name_entry = tk.Entry(name_frame, textvariable=self.name_var, font=("Times New Roman", 10), width=30)
        name_entry.pack(fill='x', pady=2)
        
        # категория
        category_frame = tk.Frame(fields_row, bg='white')
        category_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        tk.Label(category_frame, text="Категория товара*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                     font=("Times New Roman", 10), width=28)
        category_combo.pack(fill='x', pady=2)
        
        # производитель
        manufacturer_frame = tk.Frame(fields_row, bg='white')
        manufacturer_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        tk.Label(manufacturer_frame, text="Производитель*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        manufacturer_combo = ttk.Combobox(manufacturer_frame, textvariable=self.manufacturer_var, 
                                         font=("Times New Roman", 10), width=28)
        manufacturer_combo.pack(fill='x', pady=2)
        
        # количество на складе
        quantity_frame = tk.Frame(fields_row, bg='white')
        quantity_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        tk.Label(quantity_frame, text="Количество на складе*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        quantity_entry = tk.Entry(quantity_frame, textvariable=self.quantity_var, 
                                 font=("Times New Roman", 10), width=30)
        quantity_entry.pack(fill='x', pady=2)
        
        # поставщик
        supplier_frame = tk.Frame(fields_row, bg='white')
        supplier_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        tk.Label(supplier_frame, text="Поставщик*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        supplier_entry = tk.Entry(supplier_frame, textvariable=self.supplier_var, 
                                 font=("Times New Roman", 10), width=30)
        supplier_entry.pack(fill='x', pady=2)
        
        # цена
        price_frame = tk.Frame(fields_row, bg='white')
        price_frame.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)
        tk.Label(price_frame, text="Цена*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        price_entry = tk.Entry(price_frame, textvariable=self.price_var, 
                              font=("Times New Roman", 10), width=30)
        price_entry.pack(fill='x', pady=2)
        
        # единица измерения
        unit_frame = tk.Frame(fields_row, bg='white')
        unit_frame.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)
        tk.Label(unit_frame, text="Единица измерения*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        unit_entry = tk.Entry(unit_frame, textvariable=self.unit_var, 
                             font=("Times New Roman", 10), width=30)
        unit_entry.pack(fill='x', pady=2)
        
        # скидка
        discount_frame = tk.Frame(fields_row, bg='white')
        discount_frame.grid(row=1, column=2, sticky='nsew', padx=5, pady=5)
        tk.Label(discount_frame, text="Действующая скидка (%):", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        discount_entry = tk.Entry(discount_frame, textvariable=self.discount_var, 
                                 font=("Times New Roman", 10), width=30)
        discount_entry.pack(fill='x', pady=2)
        
        # описание товара 
        description_frame = tk.LabelFrame(right_column, text="Описание товара", 
                                         font=("Times New Roman", 12), bg='white', padx=10, pady=10)
        description_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.description_text = tk.Text(description_frame, font=("Times New Roman", 10), 
                                       height=8)
        self.description_text.pack(fill='both', expand=True, pady=5)
        
        # кнопки управления
        buttons_frame = tk.Frame(self.window, bg='white')
        buttons_frame.pack(fill='x', pady=20, padx=20)
        
        buttons_frame.columnconfigure(0, weight=1)  
        buttons_frame.columnconfigure(1, weight=1)  
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Отмена",
            font=("Times New Roman", 12),
            bg="#FFFFFF",
            fg='black',
            width=18,
            height=2,
            command=self.cancel
        )
        cancel_btn.grid(row=0, column=0, padx=5)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Сохранить",
            font=("Times New Roman", 12, "bold"),
            bg='#7FFF00',
            fg='black',
            width=18,
            height=2,
            command=self.save_product
        )
        save_btn.grid(row=0, column=1, padx=5)
        
        # подсказка обязательных полей
        mandatory_label = tk.Label(
            self.window,
            text="* - обязательные для заполнения поля",
            font=("Times New Roman", 10, "italic"),
            bg='white',
            fg='gray'
        )
        mandatory_label.pack(pady=(0, 10))
        
        # данные для выпадающих списков
        self.load_combobox_data(category_combo, manufacturer_combo)

    # создание следующего артикула
    def calculate_next_article(self):
        try:
            query = "SELECT article FROM products ORDER BY article"
            results = self.db.fetch_all(query)
            
            if not results:
                # Если товаров нет, начинаем с A001A1
                self.article_var.set("A001A1")
                return
            
            # получаем все артикулы
            articles = [str(r[0]) for r in results]
            
            # разбираем последний артикул
            last_article = articles[-1]
            
            # проверка формата
            if len(last_article) >= 6:
                import re
                match = re.match(r'([A-Z])(\d+)([A-Z])(\d+)', last_article)
                
                if match:
                    first_letter = match.group(1)  
                    first_num = int(match.group(2))  
                    second_letter = match.group(3)  
                    second_num = int(match.group(4))  
                    
                    # увеличиваем последнюю цифровую часть
                    second_num += 1
                    
                    # если вторая цифровая часть превысила 9, увеличиваем первую часть
                    if second_num > 9:
                        second_num = 1
                        first_num += 1
                    
                    # форматируем новое значение
                    new_first_num = f"{first_num:03d}"  
                    new_article = f"{first_letter}{new_first_num}{second_letter}{second_num}"
                    self.article_var.set(new_article)
                    return
            
            # если формат не распознан или артикул не соответствует шаблону,
            # создаем новый артикул на основе последнего существующего
            for article in reversed(articles):
                if len(article) >= 3:
                    import re
                    match = re.match(r'([A-Z])', article)
                    if match:
                        first_letter = match.group(1)
                        
                        num_match = re.search(r'\d+', article[1:])
                        if num_match:
                            first_num = int(num_match.group())
                            
                            remaining = article[1+len(num_match.group()):]
                            if remaining:
                                second_letter_match = re.match(r'([A-Z])', remaining)
                                if second_letter_match:
                                    second_letter = second_letter_match.group(1)
                                    
                                    last_num_match = re.search(r'\d+', remaining[1:])
                                    if last_num_match:
                                        second_num = int(last_num_match.group()) + 1
                                    else:
                                        second_num = 1
                                    
                                    if second_num > 9:
                                        second_num = 1
                                        first_num += 1
                                    
                                    # форматируем новое значение
                                    new_first_num = f"{first_num:03d}"
                                    new_article = f"{first_letter}{new_first_num}{second_letter}{second_num}"
                                    self.article_var.set(new_article)
                                    return
            
            # Если не удалось распознать ни один артикул, создаем новый из последнего артикула
            # путем добавления суффикса
            last_article_str = str(last_article)
            if last_article_str[-1].isdigit():
                i = len(last_article_str) - 1
                while i >= 0 and last_article_str[i].isdigit():
                    i -= 1
                prefix = last_article_str[:i+1]
                num_part = last_article_str[i+1:]
                if num_part:
                    new_num = int(num_part) + 1
                    new_article = f"{prefix}{new_num}"
                else:
                    new_article = f"{last_article_str}1"
            else:
                new_article = f"{last_article_str}1"
            
            self.article_var.set(new_article)
            
        except Exception as e:
            print(f"Error calculating next article: {e}")
            try:
                query = "SELECT COUNT(*) FROM products"
                result = self.db.fetch_one(query)
                count = result[0] if result else 0
                self.article_var.set(f"A{count+1:03d}B1")
            except:
                self.article_var.set("A001B1")
    # загрузка данных для выпадающих списков
    def load_combobox_data(self, category_combo, manufacturer_combo):
        categories = self.get_unique_values("category")
        category_combo['values'] = categories
        
        manufacturers = self.get_unique_values("manufacturer")
        manufacturer_combo['values'] = manufacturers

    # получение уникальных значений из базы данных для выпадающих списков
    def get_unique_values(self, field_name):
        try:
            if field_name == "category":
                query = "SELECT DISTINCT category FROM products ORDER BY category"
                results = self.db.fetch_all(query)
                values = [str(r[0]) for r in results] if results else []
            elif field_name == "manufacturer":
                query = "SELECT DISTINCT manufacturer FROM products ORDER BY manufacturer"
                results = self.db.fetch_all(query)
                values = [str(r[0]) for r in results] if results else []
            elif field_name == "supplier":
                query = "SELECT DISTINCT supplier FROM products ORDER BY supplier"
                results = self.db.fetch_all(query)
                values = [str(r[0]) for r in results] if results else []
            else:
                return []
            
            return values
        except Exception as e:
            print(f"Error getting unique values: {e}")
            return []
    
    def load_initial_data(self):
        # загрузка заглушки для фото
        self.load_default_photo()
    
    def load_default_photo(self):
        try:
            if not os.path.exists("resources"):
                os.makedirs("resources")
            
            self.photo_path = None
            self.photo_label.config(text="Нет фото\n(300×200)", 
                                   font=("Times New Roman", 12), 
                                   justify='center')
        except Exception as e:
            print(f"Error loading default photo: {e}")
    
    def display_photo(self, path):
        try:
            img = Image.open(path)
            
            target_width, target_height = 300, 200
            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            
            new_img = Image.new("RGB", (target_width, target_height), (240, 240, 240))
            
            x_offset = (target_width - img.width) // 2
            y_offset = (target_height - img.height) // 2
            new_img.paste(img, (x_offset, y_offset))
            
            photo = ImageTk.PhotoImage(new_img)
            self.photo_label.config(image=photo, text="")
            self.photo_label.image = photo
        except Exception as e:
            print(f"Error displaying photo: {e}")
            self.photo_label.config(text="Ошибка\nзагрузки\nфото", 
                                   font=("Times New Roman", 10),
                                   justify='center')
    
    def load_photo(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_path:
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                
                filename = f"{uuid.uuid4().hex[:8]}.{file_path.split('.')[-1].lower()}"
                destination = f"resources/{filename}"
                
                if not os.path.exists("resources"):
                    os.makedirs("resources")
                
                shutil.copy2(file_path, destination)
                
                self.photo_path = filename
                self.display_photo(destination)
                
                messagebox.showinfo("Успех", f"Фото загружено\nРазмер: {width}×{height}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить фото: {e}")
    
    def validate_fields(self):
        errors = []
        
        if not self.name_var.get().strip():
            errors.append("Наименование товара обязательно для заполнения")
        
        if not self.category_var.get().strip():
            errors.append("Категория товара обязательна для выбора")
        
        if not self.manufacturer_var.get().strip():
            errors.append("Производитель обязателен для выбора")
        
        if not self.supplier_var.get().strip():
            errors.append("Поставщик обязателен для заполнения")
        
        if not self.unit_var.get().strip():
            errors.append("Единица измерения обязательна для заполнения")
        
        # проверка цены
        price_str = self.price_var.get().strip()
        if not price_str:
            errors.append("Цена обязательна для заполнения")
        else:
            try:
                price = float(price_str)
                if price <= 0:  
                    errors.append("Цена должна быть больше 0")
                elif price > 1000000:
                    errors.append("Цена слишком большая")
            except ValueError:
                errors.append("Цена должна быть числом (например: 123.45)")
        
        # проверка количества
        quantity_str = self.quantity_var.get().strip()
        if not quantity_str:
            errors.append("Количество на складе обязательно для заполнения")
        else:
            try:
                quantity = int(quantity_str)
                if quantity < 0: 
                    errors.append("Количество не может быть отрицательным")
                elif quantity == 0:  
                    errors.append("Количество на складе не может быть равно 0")
                elif quantity > 100000:
                    errors.append("Количество слишком большое")
            except ValueError:
                errors.append("Количество должно быть целым числом")
        
        # проверка скидки
        discount_str = self.discount_var.get().strip()
        if not discount_str:  
            discount = 0.0
        else:
            try:
                discount = float(discount_str)
                if discount < 0 or discount > 100:
                    errors.append("Скидка должна быть в диапазоне от 0 до 100%")
            except ValueError:
                errors.append("Скидка должна быть числом (например: 15.5)")
        
        # проверка на уникальность артикула
        article = self.article_var.get().strip()
        check_query = "SELECT COUNT(*) FROM products WHERE article = %s"
        result = self.db.fetch_one(check_query, (article,))
        if result and result[0] > 0:
            errors.append(f"Товар с артикулом '{article}' уже существует")
        
        return errors
    
    # сохранение товара
    def save_product(self):
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Ошибки валидации", "\n".join(errors))
            return
        
        try:
            article = self.article_var.get().strip()
            name = self.name_var.get().strip()
            category = self.category_var.get().strip()
            description = self.description_text.get("1.0", "end-1c").strip()
            manufacturer = self.manufacturer_var.get().strip()
            supplier = self.supplier_var.get().strip()
            price = float(self.price_var.get().strip())
            unit = self.unit_var.get().strip()
            quantity = int(self.quantity_var.get().strip())
            
            discount_str = self.discount_var.get().strip()
            discount = float(discount_str) if discount_str else 0.0
            
            photo = self.photo_path
            
            product_data = Product(
                article=article,
                name=name,
                category=category,
                description=description,
                manufacturer=manufacturer,
                supplier=supplier,
                price=price,
                unit=unit,
                quantity=quantity,
                discount=discount,
                photo=photo
            )
            
            self.db.add_product(product_data)
            messagebox.showinfo("Успех", f"Товар '{article}' успешно добавлен!")
            
            # закрытие окно создания
            self.window.destroy()
            
            # обновление списка товаров в главном окне
            if hasattr(self.app, 'products_window'):
                self.app.products_window.refresh_products()
            elif hasattr(self.app, 'refresh_products'):
                self.app.refresh_products()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить товар: {e}")
            print(f"Save product error: {e}")

    # отмена и закрытие окна
    def cancel(self):
        self.window.destroy()