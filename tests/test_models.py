"""
Unit-тесты для модуля models.py

Тестирует основные классы Customer, Product, Order и их функциональность.
"""

import unittest
from datetime import datetime
import sys
import os

# Добавляем путь к основным модулям
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Customer, Product, Order, OrderItem, factorial, sort_customers_by_spending


class TestCustomer(unittest.TestCase):
    """Тесты для класса Customer."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.customer = Customer(
            customer_id=1,
            name="Тест Тестов",
            email="test@example.com",
            phone="+7(999)123-45-67",
            address="Тестовая улица, 1",
            city="Москва"
        )

    def test_customer_creation(self):
        """Тест создания клиента."""
        self.assertEqual(self.customer.customer_id, 1)
        self.assertEqual(self.customer.name, "Тест Тестов")
        self.assertEqual(self.customer.email, "test@example.com")
        self.assertEqual(self.customer.phone, "+7(999)123-45-67")
        self.assertEqual(self.customer.city, "Москва")

    def test_invalid_email(self):
        """Тест валидации неправильного email."""
        with self.assertRaises(ValueError):
            Customer(1, "Тест", "invalid-email", "+7(999)123-45-67")

    def test_invalid_phone(self):
        """Тест валидации неправильного телефона."""
        with self.assertRaises(ValueError):
            Customer(1, "Тест", "test@example.com", "123")

    def test_get_info(self):
        """Тест получения информации о клиенте."""
        info = self.customer.get_info()
        self.assertIsInstance(info, dict)
        self.assertEqual(info['customer_id'], 1)
        self.assertEqual(info['name'], "Тест Тестов")
        self.assertEqual(info['orders_count'], 0)
        self.assertEqual(info['total_spent'], 0)

    def test_orders_management(self):
        """Тест управления заказами клиента."""
        # Создаем тестовые объекты
        product = Product(1, "Тест товар", 100.0, "Тест", "Описание", 10)
        order = Order(1, self.customer)
        order.add_item(product, 2)

        # Добавляем заказ клиенту
        self.customer.add_order(order)

        self.assertEqual(self.customer.get_orders_count(), 1)
        self.assertEqual(self.customer.get_total_spent(), 200.0)


class TestProduct(unittest.TestCase):
    """Тесты для класса Product."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.product = Product(
            product_id=1,
            name="Тестовый товар",
            price=1500.0,
            category="Тест",
            description="Описание тестового товара",
            stock=10
        )

    def test_product_creation(self):
        """Тест создания товара."""
        self.assertEqual(self.product.product_id, 1)
        self.assertEqual(self.product.name, "Тестовый товар")
        self.assertEqual(self.product.price, 1500.0)
        self.assertEqual(self.product.stock, 10)

    def test_negative_price(self):
        """Тест отрицательной цены."""
        with self.assertRaises(ValueError):
            Product(1, "Товар", -100.0)

    def test_negative_stock(self):
        """Тест отрицательного количества на складе."""
        with self.assertRaises(ValueError):
            Product(1, "Товар", 100.0, stock=-1)

    def test_stock_management(self):
        """Тест управления складом."""
        # Тест уменьшения склада
        self.assertTrue(self.product.update_stock(-3))
        self.assertEqual(self.product.stock, 7)

        # Тест увеличения склада
        self.assertTrue(self.product.update_stock(5))
        self.assertEqual(self.product.stock, 12)

        # Тест недостатка товара на складе
        with self.assertRaises(ValueError):
            self.product.update_stock(-15)

    def test_availability(self):
        """Тест проверки доступности товара."""
        self.assertTrue(self.product.is_available(5))
        self.assertTrue(self.product.is_available(10))
        self.assertFalse(self.product.is_available(15))


class TestOrder(unittest.TestCase):
    """Тесты для класса Order."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.customer = Customer(1, "Тест", "test@example.com", "+7(999)123-45-67")
        self.product1 = Product(1, "Товар 1", 100.0, stock=10)
        self.product2 = Product(2, "Товар 2", 200.0, stock=5)
        self.order = Order(1, self.customer)

    def test_order_creation(self):
        """Тест создания заказа."""
        self.assertEqual(self.order.order_id, 1)
        self.assertEqual(self.order.customer, self.customer)
        self.assertIsInstance(self.order.order_date, datetime)
        self.assertEqual(len(self.order.items), 0)

    def test_add_items(self):
        """Тест добавления товаров в заказ."""
        self.order.add_item(self.product1, 2)
        self.order.add_item(self.product2, 1)

        self.assertEqual(len(self.order.items), 2)
        self.assertEqual(self.order.get_total(), 400.0)  # 2*100 + 1*200
        self.assertEqual(self.order.get_items_count(), 3)  # 2+1

    def test_add_unavailable_item(self):
        """Тест добавления недоступного товара."""
        with self.assertRaises(ValueError):
            self.order.add_item(self.product1, 15)  # Больше чем на складе

    def test_duplicate_item(self):
        """Тест добавления дублирующегося товара."""
        self.order.add_item(self.product1, 2)
        self.order.add_item(self.product1, 3)  # Добавляем тот же товар

        self.assertEqual(len(self.order.items), 1)  # Должна остаться одна позиция
        self.assertEqual(self.order.items[0].quantity, 5)  # Но с общим количеством 5

    def test_remove_item(self):
        """Тест удаления товара из заказа."""
        self.order.add_item(self.product1, 2)
        self.order.add_item(self.product2, 1)

        self.assertTrue(self.order.remove_item(self.product1.product_id))
        self.assertEqual(len(self.order.items), 1)
        self.assertFalse(self.order.remove_item(999))  # Несуществующий товар


class TestOrderItem(unittest.TestCase):
    """Тесты для класса OrderItem."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.product = Product(1, "Тест", 100.0, stock=10)

    def test_order_item_creation(self):
        """Тест создания позиции заказа."""
        item = OrderItem(self.product, 3)

        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.price_at_time, 100.0)
        self.assertEqual(item.get_total(), 300.0)

    def test_zero_quantity(self):
        """Тест нулевого количества."""
        with self.assertRaises(ValueError):
            OrderItem(self.product, 0)

    def test_custom_price(self):
        """Тест кастомной цены на момент заказа."""
        item = OrderItem(self.product, 2, price_at_time=150.0)

        self.assertEqual(item.price_at_time, 150.0)
        self.assertEqual(item.get_total(), 300.0)  # 2 * 150


class TestUtilityFunctions(unittest.TestCase):
    """Тесты для вспомогательных функций."""

    def test_factorial(self):
        """Тест функции факториала."""
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(1), 1)
        self.assertEqual(factorial(5), 120)

        with self.assertRaises(ValueError):
            factorial(-1)

    def test_sort_customers_by_spending(self):
        """Тест сортировки клиентов по тратам."""
        # Создаем клиентов с заказами
        customer1 = Customer(1, "Клиент1", "c1@test.com", "+7(999)111-11-11")
        customer2 = Customer(2, "Клиент2", "c2@test.com", "+7(999)222-22-22")

        product = Product(1, "Товар", 100.0, stock=20)

        # Заказы для первого клиента (300 руб)
        order1 = Order(1, customer1)
        order1.add_item(product, 3)
        customer1.add_order(order1)

        # Заказы для второго клиента (100 руб)
        order2 = Order(2, customer2)
        order2.add_item(product, 1)
        customer2.add_order(order2)

        customers = [customer1, customer2]

        # Сортировка по убыванию (по умолчанию)
        sorted_desc = sort_customers_by_spending(customers)
        self.assertEqual(sorted_desc[0], customer1)  # Клиент1 тратил больше

        # Сортировка по возрастанию
        sorted_asc = sort_customers_by_spending(customers, reverse=False)
        self.assertEqual(sorted_asc[0], customer2)  # Клиент2 тратил меньше


if __name__ == '__main__':
    # Запуск всех тестов
    unittest.main(verbosity=2)
