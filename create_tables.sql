-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    login VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Таблица товаров  
CREATE TABLE products (
    article VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    supplier VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0,
    quantity INTEGER DEFAULT 0,
    description TEXT,
    photo VARCHAR(255)
);

-- Таблица пунктов выдачи
CREATE TABLE pickup_points (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL UNIQUE
);

-- Таблица заказов
CREATE TABLE orders (
    order_number INTEGER PRIMARY KEY,
    order_articles TEXT NOT NULL,
    order_date TIMESTAMP NOT NULL,
    delivery_date TIMESTAMP NOT NULL,
    pickup_address INTEGER NOT NULL REFERENCES pickup_points(id), 
    client_name VARCHAR(100) NOT NULL,
    pickup_code VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL
);

-- Таблица элементов заказа
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_number INTEGER REFERENCES orders(order_number),
    product_article VARCHAR(20) REFERENCES products(article),
    quantity INTEGER NOT NULL
);