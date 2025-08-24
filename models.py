import re
import json
from datetime import datetime
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class Person(ABC):

    def __init__(self, name: str, email: str, phone: str):
        self._name = name
        self._email = self._validate_email(email)
        self._phone = self._validate_phone(phone)

    @property
    def name(self) -> str:
        """Получить имя."""
        return self._name

    @property
    def email(self) -> str:
        """Получить email."""
        return self._email

    @property
    def phone(self) -> str:
        """Получить телефон."""
        return self._phone

    def _validate_email(self, email: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError(f"Неверный формат email: {email}")
        return email

    def _validate_phone(self, phone: str) -> str:
        # Принимаем различные форматы: +7(xxx)xxx-xx-xx, +7xxxxxxxxxx, 8xxxxxxxxxx
        pattern = r'^(\+7|8)[\d\(\)\-\s]{10,15}$'
        clean_phone = re.sub(r'[^\d+()]', '', phone)
        if not re.match(pattern, clean_phone):
            raise ValueError(f"Неверный формат телефона: {phone}")
        return phone

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Получить информацию о человеке."""
        pass


class Customer(Person):
    """Класс для представления клиента интернет-магазина."""
    def __init__(self, customer_id: int, name: str, email: str, phone: str, address: str = "", city: str = ""):
        super().__init__(name, email, phone)
        self.customer_id = customer_id
        self.address = address
        self.city = city
        self.registration_date = datetime.now()
        self.orders = []  # Список заказов клиента

    def add_order(self, order) -> None:
        self.orders.append(order)

    def get_total_spent(self) -> float:
        return sum(order.get_total() for order in self.orders)

    def get_orders_count(self) -> int:
        return len(self.orders)

    def get_info(self) -> Dict[str, Any]:
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'registration_date': self.registration_date.isoformat(),
            'orders_count': self.get_orders_count(),
            'total_spent': self.get_total_spent()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь."""
        return self.get_info()


class Product:
    """Класс для представления товара."""

    def __init__(self, product_id: int, name: str, price: float, 
                 category: str = "", description: str = "", stock: int = 0):
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if stock < 0:
            raise ValueError("Количество на складе не может быть отрицательным")

        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.stock = stock

    def update_stock(self, quantity: int) -> bool:
        new_stock = self.stock + quantity
        if new_stock < 0:
            raise ValueError(f"Недостаточно товара на складе. Доступно: {self.stock}")
        self.stock = new_stock
        return True

    def is_available(self, quantity: int = 1) -> bool:
        return self.stock >= quantity

    def get_info(self) -> Dict[str, Any]:
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'description': self.description,
            'stock': self.stock
        }

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь."""
        return self.get_info()

    def __str__(self) -> str:
        """Строковое представление товара."""
        return f"{self.name} - {self.price}₽ (в наличии: {self.stock})"


class OrderItem:
    """Класс для представления позиции в заказе."""
    def __init__(self, product: Product, quantity: int, price_at_time: float = None):
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")

        self.product = product
        self.quantity = quantity
        self.price_at_time = price_at_time if price_at_time is not None else product.price

    def get_total(self) -> float:
        return self.price_at_time * self.quantity

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь."""
        return {
            'product_id': self.product.product_id,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price_at_time': self.price_at_time,
            'total': self.get_total()
        }


class Order:
    """Класс для представления заказа."""
    def __init__(self, order_id: int, customer: Customer, order_date: datetime = None):
        self.order_id = order_id
        self.customer = customer
        self.order_date = order_date if order_date is not None else datetime.now()
        self.items = []  # Список позиций в заказе
        self.status = "Новый"  # Статус заказа

    def add_item(self, product: Product, quantity: int) -> None:
        if not product.is_available(quantity):
            raise ValueError(f"Товар {product.name} недоступен в количестве {quantity}")

        # Проверяем, есть ли уже этот товар в заказе
        for item in self.items:
            if item.product.product_id == product.product_id:
                item.quantity += quantity
                return

        # Если товара нет в заказе, добавляем новую позицию
        order_item = OrderItem(product, quantity)
        self.items.append(order_item)

    def remove_item(self, product_id: int) -> bool:
        for i, item in enumerate(self.items):
            if item.product.product_id == product_id:
                del self.items[i]
                return True
        return False

    def get_total(self) -> float:
        return sum(item.get_total() for item in self.items)

    def get_items_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def update_status(self, new_status: str) -> None:
        self.status = new_status

    def get_info(self) -> Dict[str, Any]:
        return {
            'order_id': self.order_id,
            'customer_id': self.customer.customer_id,
            'customer_name': self.customer.name,
            'order_date': self.order_date.isoformat(),
            'status': self.status,
            'items_count': self.get_items_count(),
            'total': self.get_total(),
            'items': [item.to_dict() for item in self.items]
        }

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь."""
        return self.get_info()

    def __str__(self) -> str:
        """Строковое представление заказа."""
        return f"Заказ #{self.order_id} от {self.order_date.strftime('%Y-%m-%d')} - {self.get_total()}₽"


# Функции для демонстрации функционального программирования
def sort_customers_by_spending(customers: List[Customer], reverse: bool = True) -> List[Customer]:
    return sorted(customers, key=lambda x: x.get_total_spent(), reverse=reverse)


def filter_customers_by_city(customers: List[Customer], city: str) -> List[Customer]:
    return list(filter(lambda x: x.city.lower() == city.lower(), customers))


def calculate_total_revenue(orders: List[Order]) -> float:
    return sum(map(lambda x: x.get_total(), orders))


# Рекурсивная функция для демонстрации
def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Факториал определен только для неотрицательных чисел")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


# Пример использования декоратора для логирования
def log_method(func):
    """Декоратор для логирования вызовов методов."""
    def wrapper(*args, **kwargs):
        print(f"Вызван метод {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Метод {func.__name__} завершен")
        return result
    return wrapper


if __name__ == "__main__":
    # Пример использования классов
    try:
        # Создание клиента
        customer = Customer(1, "Иван Петров", "ivan@example.com", "+7(999)123-45-67", 
                          "ул. Ленина, 1", "Москва")

        # Создание товаров
        product1 = Product(1, "Ноутбук", 50000.0, "Электроника", "Игровой ноутбук", 10)
        product2 = Product(2, "Мышь", 1500.0, "Аксессуары", "Беспроводная мышь", 25)

        # Создание заказа
        order = Order(1, customer)
        order.add_item(product1, 1)
        order.add_item(product2, 2)

        # Добавление заказа клиенту
        customer.add_order(order)

        print("Информация о клиенте:")
        print(json.dumps(customer.get_info(), ensure_ascii=False, indent=2))
        print(f"\nИнформация о заказе:")
        print(json.dumps(order.get_info(), ensure_ascii=False, indent=2))

    except ValueError as e:
        print(f"Ошибка валидации: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
