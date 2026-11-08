# product_edit_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil
import re
import uuid
from models import Product
# окно редактирования товара
class ProductEditWindow:
    def __init__(self, parent, app, product):
    
        self.parent = parent
        self.app = app
        self.db = app.db
        self.product = product
        self.original_photo_path = None
        
        # создаем окно
        self.window = tk.Toplevel(parent)
        self.window.title(f"Редактирование товара")
        self.window.geometry("1200x650")
        self.window.resizable(False, False)
        self.window.configure(bg='white')
        self.window.transient(parent)
        self.window.grab_set()
        
        # центрируем окно
        self.center_window()
        
        # переменные для хранения данных формы
        self.article_var = tk.StringVar(value=product.article)
        self.name_var = tk.StringVar(value=product.name)
        self.category_var = tk.StringVar(value=product.category)
        self.description_var = tk.StringVar(value=product.description)
        self.manufacturer_var = tk.StringVar(value=product.manufacturer)
        self.supplier_var = tk.StringVar(value=product.supplier)
        self.price_var = tk.DoubleVar(value=float(product.price))
        self.unit_var = tk.StringVar(value=product.unit)
        self.quantity_var = tk.IntVar(value=int(product.quantity))
        self.discount_var = tk.DoubleVar(value=float(product.discount))
        self.photo_path = product.photo
        
        self.setup_ui()
        self.load_initial_data()
        
        # привязываем обработчик закрытия окна
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

    # создание интерфейса окна редактирования
    def setup_ui(self):
        self.window.configure(bg='white')
        
        # заголовок окна
        title_label = tk.Label(
            self.window,
            text=f"Редактирование товара: {self.product.article}",
            font=("Times New Roman", 16, "bold"),
            bg='white'
        )
        title_label.pack(pady=10)
        
        # основной контейнер
        main_container = tk.Frame(self.window, bg='white')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # ВЕРХНЯЯ ЧАСТЬ: фото и основные поля
        top_frame = tk.Frame(main_container, bg='white')
        top_frame.pack(fill='x', pady=(0, 10))
        
        # фото товара
        photo_section = tk.Frame(top_frame, bg='white')
        photo_section.pack(side='left', padx=(0, 20))
        
        photo_label_frame = tk.LabelFrame(photo_section, text="Фото товара (300×200)", 
                                         font=("Times New Roman", 12), bg='white', padx=10, pady=10)
        photo_label_frame.pack()
        
        self.photo_label = tk.Label(photo_label_frame, bg='lightgray', width=30, height=10)
        self.photo_label.pack()
        
        # кнопки для фото
        photo_buttons = tk.Frame(photo_label_frame, bg='white')
        photo_buttons.pack(pady=10)
        
        load_photo_btn = tk.Button(
            photo_buttons,
            text="Загрузить фото",
            font=("Times New Roman", 10),
            bg='#7FFF00',
            width=15,
            command=self.load_photo
        )
        load_photo_btn.pack(side='left', padx=5)
        
        delete_photo_btn = tk.Button(
            photo_buttons,
            text="Удалить фото",
            font=("Times New Roman", 10),
            bg='#00FA9A',
            width=15,
            command=self.delete_photo
        )
        delete_photo_btn.pack(side='left', padx=5)
        
        # артикул под фото
        article_frame = tk.LabelFrame(photo_section, text="Артикул товара", 
                                     font=("Times New Roman", 12), bg='white', padx=10, pady=10)
        article_frame.pack(pady=(15, 0), fill='x')
        
        tk.Label(article_frame, text="Артикул*:", font=("Times New Roman", 10),
                bg='white').pack(anchor='w', pady=2)
        
        article_entry = tk.Entry(article_frame, textvariable=self.article_var,
                               font=("Times New Roman", 10), width=25, state='readonly')
        article_entry.pack(pady=5)
        
        fields_section = tk.Frame(top_frame, bg='white')
        fields_section.pack(side='left', fill='both', expand=True)
        
        # колонки для полей
        for i in range(3):
            fields_section.columnconfigure(i, weight=1)
        
        # наименование товара
        name_frame = tk.Frame(fields_section, bg='white')
        name_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        tk.Label(name_frame, text="Наименование товара*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        name_entry = tk.Entry(name_frame, textvariable=self.name_var, font=("Times New Roman", 10), width=30)
        name_entry.pack(fill='x', pady=2)
        
        # категория
        category_frame = tk.Frame(fields_section, bg='white')
        category_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        tk.Label(category_frame, text="Категория товара*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                     font=("Times New Roman", 10), width=28)
        category_combo.pack(fill='x', pady=2)
        
        # производитель
        manufacturer_frame = tk.Frame(fields_section, bg='white')
        manufacturer_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        tk.Label(manufacturer_frame, text="Производитель*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        manufacturer_combo = ttk.Combobox(manufacturer_frame, textvariable=self.manufacturer_var, 
                                         font=("Times New Roman", 10), width=28)
        manufacturer_combo.pack(fill='x', pady=2)
        
        # количество на складе
        quantity_frame = tk.Frame(fields_section, bg='white')
        quantity_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        tk.Label(quantity_frame, text="Количество на складе*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        quantity_entry = tk.Entry(quantity_frame, textvariable=self.quantity_var, 
                                 font=("Times New Roman", 10), width=30)
        quantity_entry.pack(fill='x', pady=2)
        
        # поставщик
        supplier_frame = tk.Frame(fields_section, bg='white')
        supplier_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        tk.Label(supplier_frame, text="Поставщик*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        supplier_entry = tk.Entry(supplier_frame, textvariable=self.supplier_var, 
                                 font=("Times New Roman", 10), width=30)
        supplier_entry.pack(fill='x', pady=2)
        
        # цена
        price_frame = tk.Frame(fields_section, bg='white')
        price_frame.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)
        tk.Label(price_frame, text="Цена*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        price_entry = tk.Entry(price_frame, textvariable=self.price_var, 
                              font=("Times New Roman", 10), width=30)
        price_entry.pack(fill='x', pady=2)
        
        # единица измерения
        unit_frame = tk.Frame(fields_section, bg='white')
        unit_frame.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)
        tk.Label(unit_frame, text="Единица измерения*:", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        unit_entry = tk.Entry(unit_frame, textvariable=self.unit_var, 
                             font=("Times New Roman", 10), width=30)
        unit_entry.pack(fill='x', pady=2)
        
        # скидка
        discount_frame = tk.Frame(fields_section, bg='white')
        discount_frame.grid(row=1, column=2, sticky='nsew', padx=5, pady=5)
        tk.Label(discount_frame, text="Действующая скидка (%):", font=("Times New Roman", 12),
                bg='white').pack(anchor='w', pady=2)
        discount_entry = tk.Entry(discount_frame, textvariable=self.discount_var, 
                                 font=("Times New Roman", 10), width=30)
        discount_entry.pack(fill='x', pady=2)
        
        # описание товара 
        description_frame = tk.LabelFrame(fields_section, text="Описание товара", 
                                         font=("Times New Roman", 12), bg='white', padx=10, pady=10)
        description_frame.grid(row=3, column=0, columnspan=3, sticky='nsew', padx=5, pady=10)
        
        self.description_text = tk.Text(description_frame, font=("Times New Roman", 10), 
                                       height=5, width=100)
        self.description_text.pack(fill='both', expand=True, pady=5)
        
        def update_description():
            self.description_var.set(self.description_text.get("1.0", "end-1c"))
        self.description_text.bind("<KeyRelease>", lambda e: update_description())
        
        # кнопки
        buttons_frame = tk.Frame(self.window, bg='white')
        buttons_frame.pack(fill='x', pady=15, padx=20)
        
        buttons_frame.columnconfigure(0, weight=1)  
        buttons_frame.columnconfigure(1, weight=1)  
        buttons_frame.columnconfigure(2, weight=1)  
        
        if self.app.current_user.role == "Администратор":
            delete_btn = tk.Button(
                buttons_frame,
                text="Удалить товар",
                font=("Times New Roman", 12),
                bg='#00FA9A',
                fg='black',
                width=18,
                height=2,
                command=self.delete_product
            )
            delete_btn.grid(row=0, column=0, padx=5)
        else:
            tk.Frame(buttons_frame, bg='white', width=18).grid(row=0, column=0, padx=5)
        
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
        cancel_btn.grid(row=0, column=1, padx=5)
        
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
        save_btn.grid(row=0, column=2, padx=5)
        
        # подсказка обязательных полей
        mandatory_label = tk.Label(
            self.window,
            text="* - обязательные для заполнения поля",
            font=("Times New Roman", 10, "italic"),
            bg='white',
            fg='gray'
        )
        mandatory_label.pack(pady=(0, 10))
        
        # загрузка данных для выпадающих списков
        self.load_combobox_data(category_combo, manufacturer_combo)
    
    def load_combobox_data(self, category_combo, manufacturer_combo):
        """Загружает данные для выпадающих списков"""
        # категории
        categories = self.get_unique_values("category", self.product.category)
        category_combo['values'] = categories
        if self.product.category:
            category_combo.set(self.product.category)
        
        # производители
        manufacturers = self.get_unique_values("manufacturer", self.product.manufacturer)
        manufacturer_combo['values'] = manufacturers
        if self.product.manufacturer:
            manufacturer_combo.set(self.product.manufacturer)

    # для выпадающего списка
    def get_unique_values(self, field_name, current_value=None):
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
            
            if current_value and str(current_value) not in values:
                values.append(str(current_value))
                values.sort()
            
            return values
        except Exception as e:
            print(f"Error getting unique values: {e}")
            return []
    # загрузка начальных данных
    def load_initial_data(self):
        if self.product.description:
            self.description_text.delete("1.0", "end")
            self.description_text.insert("1.0", self.product.description)
        
        # загрузка фото
        self.load_product_photo()

    # загрузка фото товара
    def load_product_photo(self):
        try:
            if self.product and self.product.photo:
                self.original_photo_path = self.product.photo
                
                possible_paths = [
                    f"resources/{self.product.photo}",
                    f"resources/images/{self.product.photo}",
                    self.product.photo
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        self.photo_path = self.product.photo
                        self.display_photo(path)
                        return
                    elif self.product.photo.startswith("resources/"):
                        if os.path.exists(self.product.photo):
                            self.photo_path = self.product.photo
                            self.display_photo(self.product.photo)
                            return
            
            self.load_default_photo()
        except Exception as e:
            print(f"Error loading product photo: {e}")
            self.load_default_photo()
    # загрузка фото-заглушки
    def load_default_photo(self):
        try:
            self.photo_path = None
            self.photo_label.config(text="Нет фото\n(300×200)", 
                                   font=("Times New Roman", 12), 
                                   justify='center')
        except Exception as e:
            print(f"Error loading default photo: {e}")

    # отображение фото 300 на 200
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
    # загрузка фото 
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
    # удаление текущего фото
    def delete_photo(self):
        if messagebox.askyesno("Удаление фото", "Вы уверены, что хотите удалить текущее фото?"):
            self.photo_path = None
            self.load_default_photo()
            
            if self.original_photo_path:
                possible_paths = [
                    f"resources/{self.original_photo_path}",
                    f"resources/images/{self.original_photo_path}",
                    self.original_photo_path
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                            break
                        except Exception as e:
                            print(f"Error deleting old photo {path}: {e}")
    # валидация
    def validate_fields(self):
        errors = []
        
        if not self.article_var.get().strip():
            errors.append("Артикул товара обязателен для заполнения")
        
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
        
        try:
            price = float(self.price_var.get())
            if price <= 0:  
                errors.append("Цена должна быть больше 0")
            if price > 1000000:
                errors.append("Цена слишком большая")
        except ValueError:
            errors.append("Цена должна быть числом (например: 123.45)")
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity < 0:  
                errors.append("Количество не может быть отрицательным")
            elif quantity == 0:  
                errors.append("Количество на складе не может быть равно 0")
            if quantity > 100000:
                errors.append("Количество слишком большое")
        except ValueError:
            errors.append("Количество должно быть целым числом")
        
        try:
            discount = float(self.discount_var.get())
            if discount < 0 or discount > 100:
                errors.append("Скидка должна быть в диапазоне от 0 до 100%")
        except ValueError:
            errors.append("Скидка должна быть числом (например: 15.5)")
        
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
            price = float(self.price_var.get())
            unit = self.unit_var.get().strip()
            quantity = int(self.quantity_var.get())
            discount = float(self.discount_var.get())
            
            if self.original_photo_path:
                if (self.photo_path != self.original_photo_path and 
                    self.original_photo_path):
                    possible_paths = [
                        f"resources/{self.original_photo_path}",
                        f"resources/images/{self.original_photo_path}",
                        self.original_photo_path
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            try:
                                os.remove(path)
                                break
                            except Exception as e:
                                print(f"Error deleting old photo {path}: {e}")
            
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
            
            self.db.update_product(product_data)
            messagebox.showinfo("Успех", f"Товар успешно обновлен!")
            
            self.window.destroy()
            if hasattr(self.app, 'refresh_products'):
                self.app.refresh_products()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить товар: {e}")
            print(f"Save product error: {e}")
    # удаление товара
    def delete_product(self):
        article = self.product.article
        name = self.product.name
        
        if messagebox.askyesno("Удаление товара", 
                              f"Вы уверены, что хотите удалить товар?\n{article} - {name}\n\n"
                              "Внимание: товар, который есть в заказах, удалить нельзя."):
            try:
                success = self.db.delete_product(article)
                
                if success:
                    if self.product.photo:
                        possible_paths = [
                            f"resources/{self.product.photo}",
                            f"resources/images/{self.product.photo}",
                            self.product.photo
                        ]
                        
                        for path in possible_paths:
                            if os.path.exists(path):
                                try:
                                    os.remove(path)
                                    break
                                except Exception as e:
                                    print(f"Error deleting product photo {path}: {e}")
                    
                    messagebox.showinfo("Успех", f"Товар '{article}' успешно удален!")
                    self.window.destroy()
                    if hasattr(self.app, 'refresh_products'):
                        self.app.refresh_products()
                else:
                    messagebox.showerror("Ошибка", 
                                       "Нельзя удалить товар, который есть в заказах.\n"
                                       "Сначала удалите все связанные заказы.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить товар: {e}")
    # отмена и закрытие окна
    def cancel(self):
        self.window.destroy()