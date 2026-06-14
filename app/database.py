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

    def save_user(self, user_id: int, username: str = None, first_name: str = None):
        """Сохранить пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        conn.commit()
        conn.close()

    def add_to_cart(self, user_id: int, product_id: str, quantity: int = 1):
        """Добавить товар в корзину"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cart_items (user_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET
                quantity = quantity + ?
        ''', (user_id, product_id, quantity, quantity))
        conn.commit()
        conn.close()

    def get_cart(self, user_id: int) -> List[Dict]:
        """Получить корзину пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.category, c.quantity
            FROM cart_items c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_cart_count(self, user_id: int) -> int:
        """Получить количество товаров в корзине"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(quantity) as total
            FROM cart_items
            WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['total'] if row['total'] else 0

    def get_cart_total(self, user_id: int) -> float:
        """Получить общую сумму корзины"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(p.price * c.quantity) as total
            FROM cart_items c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['total'] if row['total'] else 0

    def clear_cart(self, user_id: int):
        """Очистить корзину"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    def remove_from_cart(self, user_id: int, product_id: str):
        """Удалить товар из корзины"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cart_items WHERE user_id = ? AND product_id = ?', (user_id, product_id))
        conn.commit()
        conn.close()

    def add_to_favorites(self, user_id: int, product_id: str):
        """Добавить в избранное"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO favorites (user_id, product_id)
            VALUES (?, ?)
        ''', (user_id, product_id))
        conn.commit()
        conn.close()

    def remove_from_favorites(self, user_id: int, product_id: str):
        """Удалить из избранного"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM favorites WHERE user_id = ? AND product_id = ?', (user_id, product_id))
        conn.commit()
        conn.close()

    def get_favorites(self, user_id: int) -> List[str]:
        """Получить список избранного"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT product_id FROM favorites WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row['product_id'] for row in rows]

    def get_favorites_with_details(self, user_id: int) -> List[Dict]:
        """Получить избранное с деталями товаров"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.category
            FROM favorites f
            JOIN products p ON f.product_id = p.id
            WHERE f.user_id = ?
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def create_order(self, user_id: int, order_data: Dict) -> int:
        """Создать заказ"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Генерируем номер заказа
        order_number = self.generate_order_number()

        cursor.execute('''
            INSERT INTO orders (
                user_id, order_number, delivery_type, address, 
                delivery_date, delivery_time, total_amount, comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, order_number, order_data['delivery_type'],
            order_data['address'], order_data['delivery_date'],
            order_data['delivery_time'], order_data['total_amount'],
            order_data.get('comment', '')
        ))

        order_id = cursor.lastrowid

        # Добавляем товары в заказ
        cart_items = self.get_cart(user_id)
        for item in cart_items:
            cursor.execute('''
                INSERT INTO order_items (
                    order_id, product_id, product_name, price, quantity, total_price
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                order_id, item['id'], item['name'],
                item['price'], item['quantity'],
                item['price'] * item['quantity']
            ))

        conn.commit()
        conn.close()

        return order_id

    def generate_order_number(self) -> str:
        """Сгенерировать уникальный номер заказа"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем текущую дату
        today = datetime.now().strftime("%Y%m%d")

        # Считаем количество заказов за сегодня
        cursor.execute('''
            SELECT COUNT(*) as count FROM orders 
            WHERE order_number LIKE ?
        ''', (f"{today}%",))
        row = cursor.fetchone()
        conn.close()

        count = row['count'] + 1
        return f"{today}-{count:04d}"

    def get_order_details(self, order_id: int) -> Dict:
        """Получить детали заказа"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_orders(self, user_id: int) -> List[Dict]:
        """Получить заказы пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM orders 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# Создаем глобальный экземпляр
db = Database()