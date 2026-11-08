import psycopg2
import pandas as pd
from config import DB_CONFIG
from models import User, Product, Order, PickupPoint

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            print("Connected to database successfully")
        except Exception as e:
            print(f"Error connecting to database: {e}")
    
    def execute_query(self, query, params=None, commit=True):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            if commit:
                self.connection.commit()
            return cursor
        except Exception as e:
            print(f"Error executing query: {e}")
            if commit:
                self.connection.rollback()
            return None
    
    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params, commit=False)
        if cursor:
            results = cursor.fetchall()
            cursor.close()
            return results
        return []
    
    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params, commit=False)
        if cursor:
            result = cursor.fetchone()
            cursor.close()
            return result
        return None
    
    # Методы для пользователей
    def get_user_by_credentials(self, login, password):
        query = "SELECT * FROM users WHERE login = %s AND password = %s"
        result = self.fetch_one(query, (login, password))
        if result:
            return User(*result)
        return None
    
    # Методы для товаров
    def get_all_products(self):
        query = "SELECT * FROM products ORDER BY article"
        results = self.fetch_all(query)
        return [Product(*result) for result in results]
    
    def get_products_with_filters(self, search_text="", supplier_filter="", sort_by=""):
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if search_text:
            query += """ AND (name ILIKE %s OR category ILIKE %s 
                     OR description ILIKE %s OR manufacturer ILIKE %s)"""
            params.extend([f"%{search_text}%"] * 4)
        
        if supplier_filter and supplier_filter != "Все поставщики":
            query += " AND supplier = %s"
            params.append(supplier_filter)
        
        if sort_by:
            if sort_by == "quantity_asc":
                query += " ORDER BY quantity ASC"
            elif sort_by == "quantity_desc":
                query += " ORDER BY quantity DESC"
            else:
                query += " ORDER BY article"
        else:
            query += " ORDER BY article"
        
        results = self.fetch_all(query, params)
        return [Product(*result) for result in results]
    
    def update_product(self, product):
        query = """UPDATE products SET name=%s, category=%s, description=%s, 
                manufacturer=%s, supplier=%s, price=%s, unit=%s, 
                quantity=%s, discount=%s, photo=%s WHERE article=%s"""
        self.execute_query(query, (
            product.name, product.category, product.description, 
            product.manufacturer, product.supplier, product.price,
            product.unit, product.quantity, product.discount,
            product.photo, product.article
        ))
    
    def add_product(self, product):
        query = """INSERT INTO products (article, name, unit, price, supplier, 
                   manufacturer, category, discount, quantity, description, photo) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.execute_query(query, (
            product.article, product.name, product.unit, product.price,
            product.supplier, product.manufacturer, product.category,
            product.discount, product.quantity, product.description, product.photo
        ))
    
    def delete_product(self, article):
        try:
            # Проверяем, есть ли товар в заказах
            check_query = "SELECT COUNT(*) FROM order_items WHERE product_article = %s"
            result = self.fetch_one(check_query, (article,))
            
            if result and result[0] > 0:
                return False  # Нельзя удалить товар, который есть в заказах
            
            delete_query = "DELETE FROM products WHERE article = %s"
            self.execute_query(delete_query, (article,))
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    def get_product_by_article(self, article):
        query = "SELECT * FROM products WHERE article = %s"
        result = self.fetch_one(query, (article,))
        if result:
            return Product(*result)
        return None
    
    def get_unique_field_values(self, field_name):
        """Получение уникальных значений для указанного поля"""
        valid_fields = ['category', 'manufacturer', 'supplier', 'unit']
        if field_name not in valid_fields:
            return []
        
        query = f"SELECT DISTINCT {field_name} FROM products WHERE {field_name} IS NOT NULL ORDER BY {field_name}"
        results = self.fetch_all(query)
        return [str(r[0]) for r in results] if results else []
    
    def get_pickup_address_by_id(self, address_id):
        """Получение текста адреса по ID"""
        try:
            # Пробуем получить адрес из pickup_points
            query = "SELECT address FROM pickup_points WHERE id = %s"
            result = self.fetch_one(query, (address_id,))
            if result and result[0]:
                return str(result[0])
        except Exception as e:
            print(f"Error getting address by ID {address_id}: {e}")
        
        return str(address_id)  # Если не нашли, возвращаем ID как строку
    
    def get_pickup_id_by_address(self, address_text):
        """Получение ID адреса по тексту"""
        try:
            # Пробуем найти существующий адрес
            query = "SELECT id FROM pickup_points WHERE address = %s"
            result = self.fetch_one(query, (address_text,))
            
            if result and result[0]:
                return result[0]
            
            # Если адрес не найден, добавляем новый
            insert_query = "INSERT INTO pickup_points (address) VALUES (%s) RETURNING id"
            cursor = self.execute_query(insert_query, (address_text,), commit=True)
            if cursor:
                result = cursor.fetchone()
                cursor.close()
                if result:
                    return result[0]
            
            # Если не удалось добавить, возвращаем текст адреса как строку
            return address_text
        except Exception as e:
            print(f"Error getting pickup ID for address '{address_text}': {e}")
            return address_text  # Возвращаем текст адреса как запасной вариант
    
    # Методы для заказов
    def get_all_orders(self):
        """Получение всех заказов с JOIN пунктов выдачи"""
        query = """
        SELECT 
            o.order_number,
            o.order_articles,
            o.order_date,
            o.delivery_date,
            p.address as pickup_address_full,  -- Полный адрес из pickup_points
            o.client_name,
            o.pickup_code,
            o.status
        FROM orders o
        LEFT JOIN pickup_points p ON o.pickup_address = p.id
        ORDER BY o.order_number
        """
        
        results = self.fetch_all(query)
        
        orders = []
        for result in results:
            order = Order(
                order_number=result[0],
                order_articles=result[1],
                order_date=result[2],
                delivery_date=result[3],
                pickup_address=result[4] if result[4] else "Адрес не указан",
                client_name=result[5],
                pickup_code=result[6],
                status=result[7]
            )
            orders.append(order)
        
        return orders
    
    def add_order(self, order):
        """Добавление нового заказа"""
        try:
            address_id = order.pickup_address
            # проверка на число
            if not isinstance(address_id, (int, float)):
                try:
                    address_id = int(address_id)
                except ValueError:
                    raise ValueError("ID пункта выдачи должен быть числом")
            
            cursor = self.connection.cursor()
            
            # вставка основного заказа
            query = """INSERT INTO orders 
                    (order_number, order_articles, order_date, delivery_date, 
                        pickup_address, client_name, pickup_code, status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(query, (
                order.order_number, order.order_articles, order.order_date,
                order.delivery_date, address_id, order.client_name,
                order.pickup_code, order.status
            ))
            
            # парсинг артикулов товаров в order_items
            if order.order_articles:
                try:
                    # парсинг строки с артикулами
                    parts = [part.strip() for part in order.order_articles.split(',')]
                    
                    if len(parts) >= 2 and len(parts) % 2 == 0:
                        for i in range(0, len(parts), 2):
                            article = parts[i]
                            quantity_str = parts[i + 1]
                            
                            try:
                                quantity = int(quantity_str)
                                
                                # проверка существует ли товар
                                product = self.get_product_by_article(article)
                                if product:
                                    # добавление записи в order_items
                                    item_query = """INSERT INTO order_items 
                                                (order_number, product_article, quantity) 
                                                VALUES (%s, %s, %s)"""
                                    cursor.execute(item_query, (order.order_number, article, quantity))
                                else:
                                    print(f"Warning: Product with article '{article}' not found in database")
                                    
                            except ValueError:
                                print(f"Warning: Invalid quantity '{quantity_str}' for article '{article}'")
                                continue
                                
                except Exception as e:
                    print(f"Error parsing order articles: {e}")
                    # если не удалось добавить товар, то откат
                    self.connection.rollback()
                    raise
            
            # коммитим
            self.connection.commit()
            cursor.close()
            
        except Exception as e:
            # откат в случае ошибки
            if 'cursor' in locals():
                cursor.close()
            self.connection.rollback()
            raise
    
    def update_order(self, order):
        """Обновление существующего заказа"""
        # находим ID адреса по тексту
        address_id = self.get_pickup_id_by_address(order.pickup_address)
        
        query = """UPDATE orders SET 
                order_articles=%s, order_date=%s, delivery_date=%s, 
                pickup_address=%s, client_name=%s, pickup_code=%s, status=%s
                WHERE order_number=%s"""
        
        self.execute_query(query, (
            order.order_articles, order.order_date, order.delivery_date,
            address_id, order.client_name, order.pickup_code,
            order.status, order.order_number
        ))
    
    def delete_order(self, order_number):
        """Удаление заказа"""
        try:
            cursor = self.connection.cursor()
            # удаление элементов заказа из order_items
            delete_items_query = "DELETE FROM order_items WHERE order_number = %s"
            cursor.execute(delete_items_query, (order_number,))
            # удаление заказа из orders
            delete_order_query = "DELETE FROM orders WHERE order_number = %s"
            cursor.execute(delete_order_query, (order_number,))
            
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error deleting order: {e}")
            if 'cursor' in locals():
                cursor.close()
            self.connection.rollback()
            return False
    
    def get_max_order_number(self):
        query = "SELECT MAX(order_number) FROM orders"
        result = self.fetch_one(query)
        return result[0] if result and result[0] else 0
    
    def get_all_pickup_points(self):
        query = "SELECT * FROM pickup_points ORDER BY address"
        results = self.fetch_all(query)
        return [PickupPoint(*result) for result in results] if results else []
    
    def get_pickup_addresses(self):
        query = "SELECT DISTINCT pickup_address FROM orders WHERE pickup_address IS NOT NULL ORDER BY pickup_address"
        results = self.fetch_all(query)
        return [str(r[0]) for r in results] if results else []
    
    def close(self):
        if self.connection:
            self.connection.close()