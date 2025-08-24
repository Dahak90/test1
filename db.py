import sqlite3
import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Union


class DatabaseManager:
    """Менеджер для работы с базой данных SQLite."""

    def __init__(self, db_path: str = "shop_database.db"):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self) -> None:
        """Создание таблиц в базе данных."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица клиентов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                address TEXT,
                city TEXT,
                registration_date TEXT NOT NULL
            )
        """)

        # Таблица товаров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT,
                description TEXT,
                stock INTEGER DEFAULT 0
            )
        """)

        # Таблица заказов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                status TEXT DEFAULT 'Новый',
                total REAL DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        """)

        # Таблица позиций в заказах
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_at_time REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        """)

        conn.commit()
        conn.close()

    def save_customer(self, customer) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO customers 
                (customer_id, name, email, phone, address, city, registration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (customer.customer_id, customer.name, customer.email, 
                 customer.phone, customer.address, customer.city,
                 customer.registration_date.isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении клиента: {e}")
            return False

    def load_customers(self):
        customers = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers')
            rows = cursor.fetchall()

            # Импортируем Customer здесь, чтобы избежать циклического импорта
            from models import Customer

            for row in rows:
                customer = Customer(
                    customer_id=row['customer_id'],
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    address=row['address'] or "",
                    city=row['city'] or ""
                )
                customer.registration_date = datetime.fromisoformat(row['registration_date'])
                customers.append(customer)

            conn.close()
        except Exception as e:
            print(f"Ошибка при загрузке клиентов: {e}")

        return customers


class FileManager:

    @staticmethod
    def export_customers_to_csv(customers, filename: str) -> bool:
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['customer_id', 'name', 'email', 'phone', 
                            'address', 'city', 'registration_date', 
                            'orders_count', 'total_spent']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for customer in customers:
                    writer.writerow(customer.get_info())

            return True
        except Exception as e:
            print(f"Ошибка при экспорте клиентов в CSV: {e}")
            return False

    @staticmethod
    def export_orders_to_json(orders, filename: str) -> bool:
        try:
            orders_data = [order.get_info() for order in orders]
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(orders_data, jsonfile, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Ошибка при экспорте заказов в JSON: {e}")
            return False


class DataRepository:

    def __init__(self, use_database: bool = True, db_path: str = "shop_database.db"):
        self.use_database = use_database
        self.db_manager = DatabaseManager(db_path) if use_database else None
        self.file_manager = FileManager()

        # Кеш данных
        self._customers = []
        self._products = []
        self._orders = []

    def load_all_data(self) -> None:
        if self.use_database and self.db_manager:
            self._customers = self.db_manager.load_customers()
            # Для упрощения, products и orders пока не реализуем полностью

    def get_customers(self):
        """Получить всех клиентов."""
        return self._customers.copy()

    def get_products(self):
        """Получить все товары."""
        return self._products.copy()

    def get_orders(self):
        """Получить все заказы."""
        return self._orders.copy()

    def add_customer(self, customer) -> bool:
        """Добавить клиента."""
        # Проверяем уникальность ID
        if any(c.customer_id == customer.customer_id for c in self._customers):
            return False

        self._customers.append(customer)
        if self.use_database and self.db_manager:
            return self.db_manager.save_customer(customer)
        return True

    def add_product(self, product) -> bool:
        """Добавить товар."""
        if any(p.product_id == product.product_id for p in self._products):
            return False
        self._products.append(product)
        return True

    def add_order(self, order) -> bool:
        """Добавить заказ."""
        if any(o.order_id == order.order_id for o in self._orders):
            return False
        self._orders.append(order)
        order.customer.add_order(order)
        return True

    def export_data(self, format_type: str = "csv", directory: str = "exports") -> bool:
        """Экспортировать данные в файлы."""
        try:
            os.makedirs(directory, exist_ok=True)

            if format_type.lower() == 'csv':
                return self.file_manager.export_customers_to_csv(
                    self._customers, os.path.join(directory, "customers.csv"))
            elif format_type.lower() == 'json':
                return self.file_manager.export_orders_to_json(
                    self._orders, os.path.join(directory, "orders.json"))

        except Exception as e:
            print(f"Ошибка при экспорте данных: {e}")

        return False


if __name__ == "__main__":
    print("Модуль db.py готов к использованию!")
