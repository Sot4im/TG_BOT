import sqlite3
import os
import random
import string
from datetime import datetime
from typing import List, Dict, Optional

# Путь к БД - из переменной окружения или по умолчанию
DB_PATH = os.getenv("DB_PATH", "/app/data/database.db")


class Database:
    def __init__(self):
        # Создаём директорию для БД, если её нет
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.init_db()

    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Создать таблицы"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица товаров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                weight TEXT
            )
        ''')

        # Таблица корзины
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (product_id) REFERENCES products(id),
                UNIQUE(user_id, product_id)
            )
        ''')

        # Таблица избранного
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, product_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'pending',
                delivery_type TEXT NOT NULL,
                address TEXT NOT NULL,
                delivery_date TEXT NOT NULL,
                delivery_time TEXT NOT NULL,
                total_amount REAL NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Таблица товаров в заказе
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER DEFAULT 1,
                total_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')

        conn.commit()
        conn.close()

        # Загружаем товары
        self.load_products()
        print(f"✅ База данных SQLite инициализирована: {DB_PATH}")

    def load_products(self):
        """Загрузить товары из products.py"""
        from app.products import PRODUCTS

        conn = self.get_connection()
        cursor = conn.cursor()

        for product_id, product in PRODUCTS.items():
            cursor.execute('''
                INSERT OR REPLACE INTO products (id, name, price, category, description, weight)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (product_id, product.name, product.price, product.category, product.description, product.weight))

        conn.commit()
        conn.close()
        print(f"✅ Загружено {len(PRODUCTS)} товаров в БД")

    # ... остальные методы остаются теми же (из предыдущего ответа)
    # get_cart, add_to_cart, get_favorites, create_order и т.д.


# Создаем глобальный экземпляр
db = Database()