"""
Unit-тесты для модуля analysis.py

Тестирует функции анализа данных, построения графиков и работы с сетями.
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Добавляем путь к основным модулям
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Customer, Product, Order
from analysis import DataAnalyzer, quicksort_orders_by_date, merge_sort_orders_by_total


class TestDataAnalyzer(unittest.TestCase):
    """Тесты для класса DataAnalyzer."""

    def setUp(self):
        """Подготовка тестовых данных."""
        # Создание клиентов
        self.customers = [
            Customer(1, "Алексей", "alex@test.com", "+7(999)111-11-11", "ул. А, 1", "Москва"),
            Customer(2, "Борис", "boris@test.com", "+7(999)222-22-22", "ул. Б, 2", "Спб"),
            Customer(3, "Вера", "vera@test.com", "+7(999)333-33-33", "ул. В, 3", "Москва")
        ]

        # Создание товаров
        self.products = [
            Product(1, "Ноутбук", 50000.0, "Техника", "Игровой ноутбук", 10),
            Product(2, "Мышь", 2000.0, "Аксессуары", "Беспроводная мышь", 20),
            Product(3, "Клавиатура", 5000.0, "Аксессуары", "Механическая", 15)
        ]

        # Создание заказов
        self.orders = []

        # Заказ 1: Алексей покупает ноутбук (50000) - 3 дня назад
        order1 = Order(1, self.customers[0], datetime.now() - timedelta(days=3))
        order1.add_item(self.products[0], 1)  # 50000
        self.orders.append(order1)
        self.customers[0].add_order(order1)

        # Заказ 2: Борис покупает мышь и клавиатуру (7000) - 2 дня назад
        order2 = Order(2, self.customers[1], datetime.now() - timedelta(days=2))
        order2.add_item(self.products[1], 1)  # 2000
        order2.add_item(self.products[2], 1)  # 5000
        self.orders.append(order2)
        self.customers[1].add_order(order2)

        # Заказ 3: Вера покупает 2 мыши (4000) - 1 день назад
        order3 = Order(3, self.customers[2], datetime.now() - timedelta(days=1))
        order3.add_item(self.products[1], 2)  # 4000
        self.orders.append(order3)
        self.customers[2].add_order(order3)

        # Создание анализатора
        self.analyzer = DataAnalyzer(self.customers, self.products, self.orders)

    def test_create_customers_dataframe(self):
        """Тест создания DataFrame клиентов."""
        df = self.analyzer.create_customers_dataframe()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertIn('customer_id', df.columns)
        self.assertIn('name', df.columns)
        self.assertIn('total_spent', df.columns)

        # Проверяем суммы трат
        alex_row = df[df['name'] == 'Алексей']
        self.assertEqual(alex_row['total_spent'].iloc[0], 50000.0)

        boris_row = df[df['name'] == 'Борис']
        self.assertEqual(boris_row['total_spent'].iloc[0], 7000.0)

    def test_create_orders_dataframe(self):
        """Тест создания DataFrame заказов."""
        df = self.analyzer.create_orders_dataframe()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertIn('order_id', df.columns)
        self.assertIn('customer_name', df.columns)
        self.assertIn('total', df.columns)

        # Проверяем суммы заказов
        order1_row = df[df['order_id'] == 1]
        self.assertEqual(order1_row['total'].iloc[0], 50000.0)

    def test_create_products_dataframe(self):
        """Тест создания DataFrame товаров."""
        df = self.analyzer.create_products_dataframe()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertIn('product_id', df.columns)
        self.assertIn('name', df.columns)
        self.assertIn('price', df.columns)

    def test_get_top_customers_by_orders(self):
        """Тест получения топ клиентов по количеству заказов."""
        df = self.analyzer.get_top_customers_by_orders(2)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertLessEqual(len(df), 2)
        self.assertIn('name', df.columns)
        self.assertIn('orders_count', df.columns)

        # У всех клиентов по 1 заказу, так что порядок может быть любой
        self.assertTrue(all(df['orders_count'] == 1))

    def test_get_top_customers_by_spending(self):
        """Тест получения топ клиентов по тратам."""
        df = self.analyzer.get_top_customers_by_spending(3)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertLessEqual(len(df), 3)

        # Алексей должен быть первым (50000)
        self.assertEqual(df.iloc[0]['name'], 'Алексей')
        self.assertEqual(df.iloc[0]['total_spent'], 50000.0)

        # Борис должен быть вторым (7000)
        self.assertEqual(df.iloc[1]['name'], 'Борис')
        self.assertEqual(df.iloc[1]['total_spent'], 7000.0)

    def test_get_sales_dynamics(self):
        """Тест получения динамики продаж."""
        df = self.analyzer.get_sales_dynamics('daily')

        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertIn('orders_count', df.columns)
        self.assertIn('total_revenue', df.columns)

        # Проверяем общую выручку
        total_revenue = df['total_revenue'].sum()
        self.assertEqual(total_revenue, 61000.0)  # 50000 + 7000 + 4000

    def test_get_product_sales_stats(self):
        """Тест статистики продаж товаров."""
        df = self.analyzer.get_product_sales_stats()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertIn('name', df.columns)
        self.assertIn('quantity_sold', df.columns)
        self.assertIn('revenue', df.columns)

        # Проверяем статистику для мыши (продано 3 штуки)
        mouse_row = df[df['name'] == 'Мышь']
        self.assertEqual(mouse_row['quantity_sold'].iloc[0], 3)  # 1 + 2
        self.assertEqual(mouse_row['revenue'].iloc[0], 6000.0)   # 2000 + 4000

    def test_empty_data(self):
        """Тест работы с пустыми данными."""
        empty_analyzer = DataAnalyzer([], [], [])

        df_customers = empty_analyzer.create_customers_dataframe()
        df_orders = empty_analyzer.create_orders_dataframe()
        df_products = empty_analyzer.create_products_dataframe()

        self.assertTrue(df_customers.empty)
        self.assertTrue(df_orders.empty)
        self.assertTrue(df_products.empty)


class TestSortingFunctions(unittest.TestCase):
    """Тесты для функций сортировки."""

    def setUp(self):
        """Подготовка тестовых данных."""
        customer = Customer(1, "Тест", "test@test.com", "+7(999)123-45-67")

        # Создаем заказы с разными датами и суммами
        self.orders = [
            Order(1, customer, datetime(2023, 1, 15)),  # Старый, 0 руб
            Order(2, customer, datetime(2023, 1, 10)),  # Старый, 0 руб
            Order(3, customer, datetime(2023, 1, 20))   # Новый, 0 руб
        ]

        # Добавляем товары для разных сумм
        product1 = Product(1, "Товар1", 100.0, stock=10)
        product2 = Product(2, "Товар2", 200.0, stock=10)
        product3 = Product(3, "Товар3", 50.0, stock=10)

        self.orders[0].add_item(product2, 1)  # 200 руб
        self.orders[1].add_item(product1, 1)  # 100 руб
        self.orders[2].add_item(product3, 1)  # 50 руб

    def test_quicksort_orders_by_date(self):
        """Тест быстрой сортировки заказов по дате."""
        # Сортировка по возрастанию даты
        sorted_asc = quicksort_orders_by_date(self.orders.copy(), reverse=False)
        dates_asc = [order.order_date for order in sorted_asc]
        self.assertEqual(dates_asc, sorted(dates_asc))

        # Сортировка по убыванию даты
        sorted_desc = quicksort_orders_by_date(self.orders.copy(), reverse=True)
        dates_desc = [order.order_date for order in sorted_desc]
        self.assertEqual(dates_desc, sorted(dates_desc, reverse=True))

    def test_merge_sort_orders_by_total(self):
        """Тест сортировки слиянием заказов по сумме."""
        # Сортировка по возрастанию суммы
        sorted_asc = merge_sort_orders_by_total(self.orders.copy(), reverse=False)
        totals_asc = [order.get_total() for order in sorted_asc]
        self.assertEqual(totals_asc, sorted(totals_asc))

        # Сортировка по убыванию суммы
        sorted_desc = merge_sort_orders_by_total(self.orders.copy(), reverse=True)
        totals_desc = [order.get_total() for order in sorted_desc]
        self.assertEqual(totals_desc, sorted(totals_desc, reverse=True))

    def test_empty_orders_list(self):
        """Тест сортировки пустого списка."""
        empty_orders = []

        result_quick = quicksort_orders_by_date(empty_orders)
        result_merge = merge_sort_orders_by_total(empty_orders)

        self.assertEqual(result_quick, [])
        self.assertEqual(result_merge, [])

    def test_single_order(self):
        """Тест сортировки списка с одним заказом."""
        single_order = [self.orders[0]]

        result_quick = quicksort_orders_by_date(single_order)
        result_merge = merge_sort_orders_by_total(single_order)

        self.assertEqual(len(result_quick), 1)
        self.assertEqual(len(result_merge), 1)
        self.assertEqual(result_quick[0], self.orders[0])
        self.assertEqual(result_merge[0], self.orders[0])


class TestNetworkAnalysis(unittest.TestCase):
    """Тесты для анализа сетей (базовые тесты без matplotlib)."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.customers = [
            Customer(1, "Клиент1", "c1@test.com", "+7(999)111-11-11", city="Москва"),
            Customer(2, "Клиент2", "c2@test.com", "+7(999)222-22-22", city="Москва"),
            Customer(3, "Клиент3", "c3@test.com", "+7(999)333-33-33", city="СПб")
        ]

        self.products = [
            Product(1, "Товар1", 100.0, stock=10),
            Product(2, "Товар2", 200.0, stock=10)
        ]

        # Создаем заказы так, чтобы клиенты были связаны через товары
        self.orders = []

        # Клиент1 и Клиент2 покупают Товар1
        order1 = Order(1, self.customers[0])
        order1.add_item(self.products[0], 1)
        self.orders.append(order1)

        order2 = Order(2, self.customers[1])
        order2.add_item(self.products[0], 1)
        self.orders.append(order2)

        # Клиент3 покупает Товар2
        order3 = Order(3, self.customers[2])
        order3.add_item(self.products[1], 1)
        self.orders.append(order3)

    def test_network_analyzer_import(self):
        """Тест импорта NetworkAnalyzer."""
        try:
            from analysis import NetworkAnalyzer
            analyzer = NetworkAnalyzer(self.customers, self.orders)
            self.assertIsNotNone(analyzer)
        except ImportError:
            self.skipTest("NetworkX не установлен")

    def test_graph_building(self):
        """Тест построения графов."""
        try:
            from analysis import NetworkAnalyzer
            analyzer = NetworkAnalyzer(self.customers, self.orders)

            # Тест графа по товарам
            product_graph = analyzer.build_customer_product_graph()
            self.assertGreater(len(product_graph.nodes()), 0)

            # Тест графа по городам
            city_graph = analyzer.build_customer_city_graph()
            self.assertGreater(len(city_graph.nodes()), 0)

        except ImportError:
            self.skipTest("NetworkX не установлен")


if __name__ == '__main__':
    # Запуск всех тестов
    unittest.main(verbosity=2)
