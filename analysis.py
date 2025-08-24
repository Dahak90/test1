import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter
import numpy as np

# Настройка matplotlib для корректного отображения русского текста
plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Настройка стиля seaborn
sns.set_style("whitegrid")
sns.set_palette("husl")


class DataAnalyzer:
    """Класс для анализа данных интернет-магазина."""

    def __init__(self, customers: List = None, products: List = None, orders: List = None):
        self.customers = customers or []
        self.products = products or []
        self.orders = orders or []

    def create_customers_dataframe(self) -> pd.DataFrame:
        if not self.customers:
            return pd.DataFrame()

        data = []
        for customer in self.customers:
            info = customer.get_info()
            data.append({
                'customer_id': info['customer_id'],
                'name': info['name'],
                'email': info['email'],
                'city': info['city'],
                'registration_date': pd.to_datetime(info['registration_date']),
                'orders_count': info['orders_count'],
                'total_spent': info['total_spent']
            })

        return pd.DataFrame(data)

    def create_orders_dataframe(self) -> pd.DataFrame:
        if not self.orders:
            return pd.DataFrame()

        data = []
        for order in self.orders:
            info = order.get_info()
            data.append({
                'order_id': info['order_id'],
                'customer_id': info['customer_id'],
                'customer_name': info['customer_name'],
                'order_date': pd.to_datetime(info['order_date']),
                'status': info['status'],
                'items_count': info['items_count'],
                'total': info['total']
            })

        return pd.DataFrame(data)

    def create_products_dataframe(self) -> pd.DataFrame:
        if not self.products:
            return pd.DataFrame()

        data = []
        for product in self.products:
            info = product.get_info()
            data.append(info)

        return pd.DataFrame(data)

    def get_top_customers_by_orders(self, top_n: int = 5) -> pd.DataFrame:
        df = self.create_customers_dataframe()
        if df.empty:
            return df

        return df.nlargest(top_n, 'orders_count')[['name', 'orders_count', 'total_spent']]

    def get_top_customers_by_spending(self, top_n: int = 5) -> pd.DataFrame:
        """
        Получить топ клиентов по потраченным средствам.
        """
        df = self.create_customers_dataframe()
        if df.empty:
            return df

        return df.nlargest(top_n, 'total_spent')[['name', 'total_spent', 'orders_count']]

    def get_sales_dynamics(self, period: str = 'daily') -> pd.DataFrame:
        df = self.create_orders_dataframe()
        if df.empty:
            return df

        df['date'] = df['order_date'].dt.date

        if period == 'weekly':
            df['period'] = df['order_date'].dt.to_period('W')
        elif period == 'monthly':
            df['period'] = df['order_date'].dt.to_period('M')
        else:  # daily
            df['period'] = df['order_date'].dt.date

        sales_dynamics = df.groupby('period').agg({
            'order_id': 'count',
            'total': 'sum',
            'items_count': 'sum'
        }).rename(columns={
            'order_id': 'orders_count',
            'total': 'total_revenue',
            'items_count': 'total_items'
        })

        return sales_dynamics.reset_index()

    def get_product_sales_stats(self) -> pd.DataFrame:
        product_stats = defaultdict(lambda: {'quantity': 0, 'revenue': 0, 'orders': 0})

        for order in self.orders:
            for item in order.items:
                product_id = item.product.product_id
                product_name = item.product.name

                product_stats[product_id]['name'] = product_name
                product_stats[product_id]['category'] = item.product.category
                product_stats[product_id]['quantity'] += item.quantity
                product_stats[product_id]['revenue'] += item.get_total()
                product_stats[product_id]['orders'] += 1

        data = []
        for product_id, stats in product_stats.items():
            data.append({
                'product_id': product_id,
                'name': stats['name'],
                'category': stats['category'],
                'quantity_sold': stats['quantity'],
                'revenue': stats['revenue'],
                'orders_count': stats['orders']
            })

        return pd.DataFrame(data).sort_values('revenue', ascending=False)


class ChartGenerator:
    """Класс для создания графиков и визуализаций."""

    def __init__(self, analyzer: DataAnalyzer):
        self.analyzer = analyzer

    def plot_top_customers(self, by: str = 'orders', top_n: int = 5, 
                          figsize: Tuple[int, int] = (10, 6)) -> None:

        if by == 'spending':
            df = self.analyzer.get_top_customers_by_spending(top_n)
            y_column = 'total_spent'
            title = f'Топ {top_n} клиентов по потраченным средствам'
            ylabel = 'Потрачено (₽)'
        else:
            df = self.analyzer.get_top_customers_by_orders(top_n)
            y_column = 'orders_count'
            title = f'Топ {top_n} клиентов по количеству заказов'
            ylabel = 'Количество заказов'

        if df.empty:
            print("Нет данных для построения графика")
            return

        plt.figure(figsize=figsize)
        bars = plt.bar(range(len(df)), df[y_column], color='skyblue', edgecolor='navy')

        # Добавляем значения на столбцы
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom')

        plt.xlabel('Клиенты')
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(range(len(df)), df['name'], rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def plot_sales_dynamics(self, period: str = 'daily', 
                           figsize: Tuple[int, int] = (12, 6)) -> None:

        df = self.analyzer.get_sales_dynamics(period)
        if df.empty:
            print("Нет данных для построения графика динамики продаж")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

        # График количества заказов
        ax1.plot(df['period'], df['orders_count'], marker='o', linewidth=2, 
                markersize=6, color='blue')
        ax1.set_ylabel('Количество заказов')
        ax1.set_title(f'Динамика продаж ({period})')
        ax1.grid(True, alpha=0.3)

        # График выручки
        ax2.plot(df['period'], df['total_revenue'], marker='s', linewidth=2, 
                markersize=6, color='green')
        ax2.set_ylabel('Выручка (₽)')
        ax2.set_xlabel('Период')
        ax2.grid(True, alpha=0.3)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_product_sales_pie(self, top_n: int = 8, figsize: Tuple[int, int] = (10, 8)) -> None:

        df = self.analyzer.get_product_sales_stats()
        if df.empty:
            print("Нет данных для построения графика продаж товаров")
            return

        # Берем топ товаров и объединяем остальные в "Другие"
        top_products = df.head(top_n-1)
        other_revenue = df.iloc[top_n-1:]['revenue'].sum()

        labels = top_products['name'].tolist()
        sizes = top_products['revenue'].tolist()

        if other_revenue > 0:
            labels.append('Другие')
            sizes.append(other_revenue)

        plt.figure(figsize=figsize)
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

        wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          colors=colors, startangle=90)

        # Улучшаем читаемость текста
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        plt.title(f'Распределение выручки по товарам (топ {len(labels)})')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def plot_customer_city_distribution(self, figsize: Tuple[int, int] = (10, 6)) -> None:
        df = self.analyzer.create_customers_dataframe()
        if df.empty:
            print("Нет данных для построения графика распределения по городам")
            return

        city_counts = df['city'].value_counts().head(10)  # Топ 10 городов

        plt.figure(figsize=figsize)
        bars = plt.bar(range(len(city_counts)), city_counts.values, 
                      color='lightcoral', edgecolor='darkred')

        # Добавляем значения на столбцы
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')

        plt.xlabel('Города')
        plt.ylabel('Количество клиентов')
        plt.title('Распределение клиентов по городам (топ 10)')
        plt.xticks(range(len(city_counts)), city_counts.index, rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


class NetworkAnalyzer:
    """Класс для анализа связей между клиентами."""

    def __init__(self, customers: List, orders: List):
        """
        Инициализация анализатора сетей.
        """
        self.customers = customers
        self.orders = orders

    def build_customer_product_graph(self) -> nx.Graph:
        G = nx.Graph()

        # Словарь товар -> список клиентов
        product_customers = defaultdict(list)

        # Заполняем информацию о покупках
        for order in self.orders:
            customer_id = order.customer.customer_id
            for item in order.items:
                product_id = item.product.product_id
                if customer_id not in product_customers[product_id]:
                    product_customers[product_id].append(customer_id)

        # Добавляем узлы (клиентов)
        for customer in self.customers:
            G.add_node(customer.customer_id, name=customer.name, city=customer.city)

        # Добавляем ребра между клиентами, купившими одинаковые товары
        for product_id, customers_list in product_customers.items():
            for i in range(len(customers_list)):
                for j in range(i + 1, len(customers_list)):
                    customer1, customer2 = customers_list[i], customers_list[j]
                    if G.has_edge(customer1, customer2):
                        G[customer1][customer2]['weight'] += 1
                    else:
                        G.add_edge(customer1, customer2, weight=1)

        return G

    def build_customer_city_graph(self) -> nx.Graph:
        G = nx.Graph()

        # Группируем клиентов по городам
        city_customers = defaultdict(list)
        for customer in self.customers:
            if customer.city:  # Только клиенты с указанным городом
                city_customers[customer.city].append(customer.customer_id)
                G.add_node(customer.customer_id, name=customer.name, city=customer.city)

        # Соединяем клиентов из одного города
        for city, customers_list in city_customers.items():
            for i in range(len(customers_list)):
                for j in range(i + 1, len(customers_list)):
                    customer1, customer2 = customers_list[i], customers_list[j]
                    G.add_edge(customer1, customer2, city=city)

        return G

    def plot_customer_network(self, graph_type: str = 'product', figsize: Tuple[int, int] = (12, 8)) -> None:
        if graph_type == 'city':
            G = self.build_customer_city_graph()
            title = 'Граф связей клиентов по городам'
        else:
            G = self.build_customer_product_graph()
            title = 'Граф связей клиентов по общим товарам'

        if len(G.nodes()) == 0:
            print("Недостаточно данных для построения графа")
            return

        plt.figure(figsize=figsize)

        # Компоновка узлов
        pos = nx.spring_layout(G, k=1, iterations=50)

        # Рисуем узлы
        node_sizes = [G.degree(node) * 300 + 100 for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                              node_color='lightblue', alpha=0.7)

        # Рисуем ребра
        nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')

        # Добавляем подписи узлов (имена клиентов)
        labels = {node: G.nodes[node].get('name', str(node)) for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.show()

        # Выводим статистику графа
        print(f"Узлов в графе: {len(G.nodes())}")
        print(f"Ребер в графе: {len(G.edges())}")
        print(f"Плотность графа: {nx.density(G):.3f}")

        if len(G.nodes()) > 0:
            degree_centrality = nx.degree_centrality(G)
            most_connected = max(degree_centrality, key=degree_centrality.get)
            print(f"Самый связанный клиент: {labels.get(most_connected, most_connected)}")


# Функции для сортировки с использованием различных алгоритмов
def quicksort_orders_by_date(orders: List, reverse: bool = False) -> List:
    if len(orders) <= 1:
        return orders

    pivot = orders[len(orders) // 2]
    pivot_date = pivot.order_date

    if reverse:
        left = [x for x in orders if x.order_date > pivot_date]
        middle = [x for x in orders if x.order_date == pivot_date]
        right = [x for x in orders if x.order_date < pivot_date]
    else:
        left = [x for x in orders if x.order_date < pivot_date]
        middle = [x for x in orders if x.order_date == pivot_date]
        right = [x for x in orders if x.order_date > pivot_date]

    return (quicksort_orders_by_date(left, reverse) + 
           middle + 
           quicksort_orders_by_date(right, reverse))


def merge_sort_orders_by_total(orders: List, reverse: bool = False) -> List:
    if len(orders) <= 1:
        return orders

    mid = len(orders) // 2
    left = merge_sort_orders_by_total(orders[:mid], reverse)
    right = merge_sort_orders_by_total(orders[mid:], reverse)

    return merge_two_sorted_lists(left, right, reverse)


def merge_two_sorted_lists(left: List, right: List, reverse: bool = False) -> List:
    result = []
    i, j = 0, 0

    while i < len(left) and j < len(right):
        if reverse:
            if left[i].get_total() >= right[j].get_total():
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        else:
            if left[i].get_total() <= right[j].get_total():
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


# Пример функции высшего порядка
def apply_discount(orders: List, discount_func) -> List:
    return list(map(discount_func, orders))


if __name__ == "__main__":
    print("Модуль анализа данных готов к использованию!")
    print("Доступные классы:")
    print("- DataAnalyzer: анализ данных")
    print("- ChartGenerator: создание графиков")
    print("- NetworkAnalyzer: анализ связей")
    print("- Функции сортировки: quicksort_orders_by_date, merge_sort_orders_by_total")
