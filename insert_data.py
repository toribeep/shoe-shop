# insert_data.py
import pandas as pd
import psycopg2
from config import DB_CONFIG
from datetime import datetime

def parse_order_articles(articles_str):
    items = []
    if pd.isna(articles_str):
        return items
    
    parts = str(articles_str).split(',')
    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            article = parts[i].strip()
            try:
                quantity = int(parts[i + 1].strip())
                items.append((article, quantity))
            except ValueError:
                print(f"Warning: Invalid quantity for article {article}: {parts[i + 1]}")
    return items

# соответствие чисел из Excel заказов строкам из файла пунктов выдачи
EXCEL_NUMBER_TO_ADDRESS = {
    1: "420151, г. Лесной, ул. Вишневая, 32",
    2: "125061, г. Лесной, ул. Подгорная, 8",
    3: "630370, г. Лесной, ул. Шоссейная, 24",
    4: "400562, г. Лесной, ул. Зеленая, 32",
    5: "614510, г. Лесной, ул. Маяковского, 47",
    6: "410542, г. Лесной, ул. Светлая, 46",
    7: "620839, г. Лесной, ул. Цветочная, 8",
    8: "443890, г. Лесной, ул. Коммунистическая, 1",
    9: "603379, г. Лесной, ул. Спортивная, 46",
    10: "603721, г. Лесной, ул. Гоголя, 41",
    11: "410172, г. Лесной, ул. Северная, 13",
    12: "614611, г. Лесной, ул. Молодежная, 50",
    13: "454311, г.Лесной, ул. Новая, 19",
    14: "660007, г.Лесной, ул. Октябрьская, 19",
    15: "603036, г. Лесной, ул. Садовая, 4",
    16: "394060, г.Лесной, ул. Фрунзе, 43",
    17: "410661, г. Лесной, ул. Школьная, 50",
    18: "625590, г. Лесной, ул. Коммунистическая, 20",
    19: "625683, г. Лесной, ул. 8 Марта",
    20: "450983, г.Лесной, ул. Комсомольская, 26",
    21: "394782, г. Лесной, ул. Чехова, 3",
    22: "603002, г. Лесной, ул. Дзержинского, 28",
    23: "450558, г. Лесной, ул. Набережная, 30",
    24: "344288, г. Лесной, ул. Чехова, 1",
    25: "614164, г.Лесной,  ул. Степная, 30",
    26: "394242, г. Лесной, ул. Коммунистическая, 43",
    27: "660540, г. Лесной, ул. Солнечная, 25",
    28: "125837, г. Лесной, ул. Шоссейная, 40",
    29: "125703, г. Лесной, ул. Партизанская, 49",
    30: "625283, г. Лесной, ул. Победы, 46",
    31: "614753, г. Лесной, ул. Полевая, 35",
    32: "426030, г. Лесной, ул. Маяковского, 44",
    33: "450375, г. Лесной ул. Клубная, 44",
    34: "625560, г. Лесной, ул. Некрасова, 12",
    35: "630201, г. Лесной, ул. Комсомольская, 17",
    36: "190949, г. Лесной, ул. Мичурина, 26"
}

def import_data():
    conn = None
    cursor = None
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # проверка на наличие существующих данных
        cursor.execute("SELECT COUNT(*) FROM pickup_points")
        existing_points = cursor.fetchone()[0]
        
        if existing_points > 0:
            print(f"В таблице pickup_points уже есть {existing_points} записей")
            choice = input("   Продолжить импорт? (y/n): ")
            if choice.lower() != 'y':
                print("   Импорт отменен")
                return
        else:
            print("Таблицы пусты, можно импортировать")
        
        # импорт пунктов выдачи
        point_id_mapping = {}
        
        for excel_number, address in EXCEL_NUMBER_TO_ADDRESS.items():
            try:
                # проверка, есть ли такой адрес
                cursor.execute("SELECT id FROM pickup_points WHERE address = %s", (address,))
                existing = cursor.fetchone()
                
                if existing:
                    point_id = existing[0]
                    print(f"   Пункт {excel_number:2d} уже существует: ID {point_id:2d}")
                else:
                    cursor.execute(
                        "INSERT INTO pickup_points (address) VALUES (%s) RETURNING id",
                        (address,)
                    )
                    point_id = cursor.fetchone()[0]
                    print(f"   Пункт {excel_number:2d} создан: ID {point_id:2d}")
                
                point_id_mapping[excel_number] = point_id
                point_id_mapping[str(excel_number)] = point_id
                
            except Exception as e:
                print(f"Ошибка при обработке пункта {excel_number}: {e}")
        
        conn.commit()
        
        # импорт пользователей 
        users_df = pd.read_excel('data/user_import.xlsx')
        user_count = 0
        
        for _, row in users_df.iterrows():
            try:
                cursor.execute("SELECT id FROM users WHERE login = %s", (row['Логин'],))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO users (role, full_name, login, password) VALUES (%s, %s, %s, %s)",
                        (row['Роль сотрудника'], row['ФИО'], row['Логин'], row['Пароль'])
                    )
                    user_count += 1
            except Exception as e:
                print(f"Ошибка при импорте пользователя {row['ФИО']}: {e}")
        
        conn.commit()
        print(f"Добавлено {user_count} новых пользователей")
        
        # импорт товаров 
        products_df = pd.read_excel('data/Tovar.xlsx')
        product_count = 0
        
        for _, row in products_df.iterrows():
            try:
                article = str(row['Артикул']) if not pd.isna(row['Артикул']) else ""
                if not article:
                    continue
                    
                cursor.execute("SELECT article FROM products WHERE article = %s", (article,))
                if not cursor.fetchone():
                    name = str(row['Наименование товара']) if not pd.isna(row['Наименование товара']) else ""
                    unit = str(row['Единица измерения']) if not pd.isna(row['Единица измерения']) else "шт"
                    price = float(row['Цена']) if not pd.isna(row['Цена']) else 0.0
                    supplier = str(row['Поставщик']) if not pd.isna(row['Поставщик']) else ""
                    manufacturer = str(row['Производитель']) if not pd.isna(row['Производитель']) else ""
                    category = str(row['Категория товара']) if not pd.isna(row['Категория товара']) else ""
                    discount = float(row['Действующая скидка']) if not pd.isna(row['Действующая скидка']) else 0.0
                    quantity = int(row['Кол-во на складе']) if not pd.isna(row['Кол-во на складе']) else 0
                    description = str(row['Описание товара']) if not pd.isna(row['Описание товара']) else ""
                    photo = str(row['Фото']) if not pd.isna(row['Фото']) else None
                    
                    cursor.execute(
                        """INSERT INTO products (article, name, unit, price, supplier, 
                           manufacturer, category, discount, quantity, description, photo) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (article, name, unit, price, supplier, manufacturer,
                         category, discount, quantity, description, photo)
                    )
                    product_count += 1
            except Exception as e:
                print(f"Ошибка при импорте товара {row.get('Артикул', 'N/A')}: {e}")
        
        conn.commit()
        print(f"Добавлено {product_count} новых товаров")
        
        # импорт заказов
        orders_df = pd.read_excel('data/Заказ_import.xlsx')
        order_count = 0
        order_item_count = 0
        
        for _, row in orders_df.iterrows():
            try:
                order_number = int(row['Номер заказа']) if not pd.isna(row['Номер заказа']) else 0
                
                # проверка существует ли такой заказ
                cursor.execute("SELECT order_number FROM orders WHERE order_number = %s", (order_number,))
                if cursor.fetchone():
                    print(f"Заказ {order_number} уже существует, пропускаем")
                    continue
                
                # преобразование даты
                try:
                    order_date = datetime.strptime(str(row['Дата заказа']), '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        order_date = datetime.strptime(str(row['Дата заказа']), '%d.%m.%Y')
                    except:
                        order_date = datetime.now()
                
                try:
                    delivery_date = datetime.strptime(str(row['Дата доставки']), '%Y-%m-%d %H:%M:%S')
                except:
                    delivery_date = datetime.now()
                
                order_articles = str(row['Артикул заказа']) if not pd.isna(row['Артикул заказа']) else ""
                client_name = str(row['ФИО авторизированного клиента']) if not pd.isna(row['ФИО авторизированного клиента']) else ""
                pickup_code = str(row['Код для получения']) if not pd.isna(row['Код для получения']) else ""
                status = str(row['Статус заказа']) if not pd.isna(row['Статус заказа']) else "Новый"
                
                # ID пункта выдачи
                excel_point_number = None
                if not pd.isna(row['Адрес пункта выдачи']):
                    try:
                        excel_point_number = int(float(row['Адрес пункта выдачи']))
                    except:
                        excel_point_number = str(row['Адрес пункта выдачи']).strip()
                
                pickup_address_id = None
                if excel_point_number and excel_point_number in point_id_mapping:
                    pickup_address_id = point_id_mapping[excel_point_number]
                else:
                    if point_id_mapping:
                        pickup_address_id = list(point_id_mapping.values())[0]
                    else:
                        pickup_address_id = 1
                
                cursor.execute(
                    """INSERT INTO orders (order_number, order_articles, order_date, 
                       delivery_date, pickup_address, client_name, pickup_code, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (order_number, order_articles, order_date,
                     delivery_date, pickup_address_id, client_name,
                     pickup_code, status)
                )
                order_count += 1
                
                # элементы заказа
                items = parse_order_articles(order_articles)
                for article, quantity in items:
                    try:
                        cursor.execute(
                            "INSERT INTO order_items (order_number, product_article, quantity) VALUES (%s, %s, %s)",
                            (order_number, article, quantity)
                        )
                        order_item_count += 1
                    except Exception as e:
                        print(f"Ошибка при импорте элемента заказа {article}: {e}")
                        
            except Exception as e:
                print(f"Ошибка при импорте заказа {row.get('Номер заказа', 'N/A')}: {e}")
        
        conn.commit()
        print(f"   Пунктов выдачи в базе: {len(point_id_mapping)//2}")
        print(f"   Добавлено пользователей: {user_count}")
        print(f"   Добавлено товаров: {product_count}")
        print(f"   Добавлено заказов: {order_count}")
        print(f"   Элементов заказов: {order_item_count}")
        
    except FileNotFoundError as e:
        print(f"Файл не найден: {e}")
        print("Убедитесь, что файлы находятся в папке 'data/':")
        print("  - user_import.xlsx")
        print("  - Tovar.xlsx")
        print("  - Заказ_import.xlsx")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    import_data()