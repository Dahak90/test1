import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

# Импорт наших модулей
try:
    from models import Customer, Product, Order
    from db import DataRepository
    from analysis import DataAnalyzer, ChartGenerator, NetworkAnalyzer
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")


class ShopManagerGUI:
    """Основной класс графического интерфейса."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Менеджер интернет-магазина")
        self.root.geometry("1200x800")

        # Инициализация репозитория данных
        self.repository = DataRepository()
        self.repository.load_all_data()

        # Создание интерфейса
        self.create_menu()
        self.create_main_interface()

        # Загружаем данные при запуске
        self.refresh_all_data()

    def create_menu(self) -> None:
        """Создание главного меню."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт данных", command=self.export_data)
        file_menu.add_command(label="Импорт данных", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Анализ"
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Анализ", menu=analysis_menu)
        analysis_menu.add_command(label="Топ клиенты", command=self.show_top_customers)
        analysis_menu.add_command(label="Динамика продаж", command=self.show_sales_dynamics)
        analysis_menu.add_command(label="Анализ товаров", command=self.show_product_analysis)
        analysis_menu.add_command(label="Граф связей", command=self.show_network_analysis)

    def create_main_interface(self) -> None:
        """Создание основного интерфейса с вкладками."""
        # Создаем notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка клиентов
        self.customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_frame, text="Клиенты")
        self.create_customers_tab()

        # Вкладка товаров
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Товары")
        self.create_products_tab()

        # Вкладка заказов
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Заказы")
        self.create_orders_tab()

        # Вкладка аналитики
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Аналитика")
        self.create_analytics_tab()

    def create_customers_tab(self) -> None:
        """Создание вкладки для работы с клиентами."""
        # Фрейм для формы добавления клиента
        add_frame = ttk.LabelFrame(self.customers_frame, text="Добавить клиента")
        add_frame.pack(fill=tk.X, padx=5, pady=5)

        # Поля формы
        ttk.Label(add_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.customer_id_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.customer_id_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(add_frame, text="Имя:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.customer_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.customer_name_var, width=20).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(add_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.customer_email_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.customer_email_var, width=25).grid(row=1, column=1, columnspan=2, padx=5, pady=2)

        ttk.Label(add_frame, text="Телефон:").grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        self.customer_phone_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.customer_phone_var, width=15).grid(row=1, column=4, padx=5, pady=2)

        ttk.Label(add_frame, text="Адрес:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.customer_address_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.customer_address_var, width=30).grid(row=2, column=1, columnspan=2, padx=5, pady=2)

        ttk.Label(add_frame, text="Город:").grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)
        self.customer_city_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.customer_city_var, width=15).grid(row=2, column=4, padx=5, pady=2)

        # Кнопка добавления
        ttk.Button(add_frame, text="Добавить клиента", 
                  command=self.add_customer).grid(row=3, column=0, columnspan=5, pady=10)

        # Фрейм для списка клиентов
        list_frame = ttk.LabelFrame(self.customers_frame, text="Список клиентов")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создание таблицы клиентов
        columns = ('ID', 'Имя', 'Email', 'Телефон', 'Город', 'Заказов', 'Потрачено')
        self.customers_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        # Настройка столбцов
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=100)

        # Добавление скроллбара
        scrollbar_customers = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                          command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar_customers.set)

        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_customers.pack(side=tk.RIGHT, fill=tk.Y)

        # Фрейм для поиска и фильтрации
        search_frame = ttk.Frame(self.customers_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
        self.customer_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.customer_search_var)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', lambda e: self.filter_customers())

        ttk.Button(search_frame, text="Обновить", command=self.refresh_customers).pack(side=tk.RIGHT, padx=5)

    def create_products_tab(self) -> None:
        """Создание вкладки для работы с товарами."""
        # Фрейм для формы добавления товара
        add_frame = ttk.LabelFrame(self.products_frame, text="Добавить товар")
        add_frame.pack(fill=tk.X, padx=5, pady=5)

        # Поля формы
        ttk.Label(add_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_id_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.product_id_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(add_frame, text="Название:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.product_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.product_name_var, width=25).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(add_frame, text="Цена:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_price_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.product_price_var, width=15).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(add_frame, text="Категория:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.product_category_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.product_category_var, width=20).grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(add_frame, text="Количество:").grid(row=1, column=4, sticky=tk.W, padx=5, pady=2)
        self.product_stock_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.product_stock_var, width=10).grid(row=1, column=5, padx=5, pady=2)

        ttk.Label(add_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_description_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.product_description_var, width=50).grid(row=2, column=1, columnspan=4, padx=5, pady=2)

        # Кнопка добавления
        ttk.Button(add_frame, text="Добавить товар", 
                  command=self.add_product).grid(row=3, column=0, columnspan=6, pady=10)

        # Фрейм для списка товаров
        list_frame = ttk.LabelFrame(self.products_frame, text="Список товаров")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создание таблицы товаров
        columns = ('ID', 'Название', 'Цена', 'Категория', 'На складе')
        self.products_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        # Настройка столбцов
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=120)

        # Добавление скроллбара
        scrollbar_products = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar_products.set)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_products.pack(side=tk.RIGHT, fill=tk.Y)

        # Фрейм для управления товарами
        control_frame = ttk.Frame(self.products_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Обновить склад", command=self.update_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", command=self.refresh_products).pack(side=tk.RIGHT, padx=5)

    def create_orders_tab(self) -> None:
        """Создание вкладки для работы с заказами."""
        # Фрейм для создания заказа
        create_frame = ttk.LabelFrame(self.orders_frame, text="Создать заказ")
        create_frame.pack(fill=tk.X, padx=5, pady=5)

        # Выбор клиента
        ttk.Label(create_frame, text="Клиент:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(create_frame, textvariable=self.order_customer_var, width=30)
        self.customer_combo.grid(row=0, column=1, padx=5, pady=2)

        # ID заказа
        ttk.Label(create_frame, text="ID заказа:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.order_id_var = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.order_id_var, width=10).grid(row=0, column=3, padx=5, pady=2)

        # Выбор товара
        ttk.Label(create_frame, text="Товар:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(create_frame, textvariable=self.order_product_var, width=30)
        self.product_combo.grid(row=1, column=1, padx=5, pady=2)

        # Количество
        ttk.Label(create_frame, text="Количество:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.order_quantity_var = tk.StringVar(value="1")
        ttk.Entry(create_frame, textvariable=self.order_quantity_var, width=10).grid(row=1, column=3, padx=5, pady=2)

        # Кнопки управления
        buttons_frame = ttk.Frame(create_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(buttons_frame, text="Добавить товар в заказ", command=self.add_item_to_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Создать заказ", command=self.create_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Очистить", command=self.clear_order_form).pack(side=tk.LEFT, padx=5)

        # Список товаров в текущем заказе
        current_order_frame = ttk.LabelFrame(self.orders_frame, text="Текущий заказ")
        current_order_frame.pack(fill=tk.X, padx=5, pady=5)

        self.current_order_text = ScrolledText(current_order_frame, height=4, width=80)
        self.current_order_text.pack(padx=5, pady=5)

        # Фрейм для списка заказов
        list_frame = ttk.LabelFrame(self.orders_frame, text="Список заказов")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создание таблицы заказов
        columns = ('ID', 'Клиент', 'Дата', 'Статус', 'Товаров', 'Сумма')
        self.orders_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        # Настройка столбцов
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=100)

        # Добавление скроллбара
        scrollbar_orders = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                       command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar_orders.set)

        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_orders.pack(side=tk.RIGHT, fill=tk.Y)

        # Инициализация текущего заказа
        self.current_order_items = []

    def create_analytics_tab(self) -> None:
        """Создание вкладки аналитики."""
        # Фрейм для кнопок анализа
        buttons_frame = ttk.LabelFrame(self.analytics_frame, text="Инструменты анализа")
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        # Первая строка кнопок
        row1 = ttk.Frame(buttons_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(row1, text="Топ клиенты по заказам", command=lambda: self.show_analytics_chart("top_customers_orders")).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="Топ клиенты по тратам", command=lambda: self.show_analytics_chart("top_customers_spending")).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="Динамика продаж", command=lambda: self.show_analytics_chart("sales_dynamics")).pack(side=tk.LEFT, padx=5)

        # Вторая строка кнопок
        row2 = ttk.Frame(buttons_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(row2, text="Продажи по товарам", command=lambda: self.show_analytics_chart("product_sales")).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="Распределение по городам", command=lambda: self.show_analytics_chart("city_distribution")).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="Граф связей клиентов", command=lambda: self.show_analytics_chart("customer_network")).pack(side=tk.LEFT, padx=5)

        # Фрейм для отображения статистики
        stats_frame = ttk.LabelFrame(self.analytics_frame, text="Статистика")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.stats_text = ScrolledText(stats_frame, height=20, width=80)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Кнопка обновления статистики
        ttk.Button(stats_frame, text="Обновить статистику", command=self.update_statistics).pack(pady=5)

    def add_customer(self) -> None:
        """Добавить нового клиента."""
        try:
            customer_id = int(self.customer_id_var.get())
            name = self.customer_name_var.get().strip()
            email = self.customer_email_var.get().strip()
            phone = self.customer_phone_var.get().strip()
            address = self.customer_address_var.get().strip()
            city = self.customer_city_var.get().strip()

            if not all([name, email, phone]):
                messagebox.showerror("Ошибка", "Заполните обязательные поля: Имя, Email, Телефон")
                return

            customer = Customer(customer_id, name, email, phone, address, city)

            if self.repository.add_customer(customer):
                messagebox.showinfo("Успех", "Клиент успешно добавлен!")
                self.clear_customer_form()
                self.refresh_customers()
                self.update_customer_combo()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить клиента (возможно, ID уже существует)")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка валидации: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def add_product(self) -> None:
        """Добавить новый товар."""
        try:
            product_id = int(self.product_id_var.get())
            name = self.product_name_var.get().strip()
            price = float(self.product_price_var.get())
            category = self.product_category_var.get().strip()
            description = self.product_description_var.get().strip()
            stock = int(self.product_stock_var.get() or "0")

            if not name:
                messagebox.showerror("Ошибка", "Введите название товара")
                return

            product = Product(product_id, name, price, category, description, stock)

            if self.repository.add_product(product):
                messagebox.showinfo("Успех", "Товар успешно добавлен!")
                self.clear_product_form()
                self.refresh_products()
                self.update_product_combo()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить товар (возможно, ID уже существует)")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка ввода данных: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def clear_customer_form(self) -> None:
        """Очистить форму клиента."""
        self.customer_id_var.set("")
        self.customer_name_var.set("")
        self.customer_email_var.set("")
        self.customer_phone_var.set("")
        self.customer_address_var.set("")
        self.customer_city_var.set("")

    def clear_product_form(self) -> None:
        """Очистить форму товара."""
        self.product_id_var.set("")
        self.product_name_var.set("")
        self.product_price_var.set("")
        self.product_category_var.set("")
        self.product_description_var.set("")
        self.product_stock_var.set("")

    def refresh_customers(self) -> None:
        """Обновить список клиентов."""
        # Очищаем таблицу
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)

        # Заполняем таблицу
        customers = self.repository.get_customers()
        for customer in customers:
            info = customer.get_info()
            self.customers_tree.insert('', tk.END, values=(
                info['customer_id'],
                info['name'],
                info['email'],
                info['phone'],
                info['city'],
                info['orders_count'],
                f"{info['total_spent']:.2f} ₽"
            ))

    def refresh_products(self) -> None:
        """Обновить список товаров."""
        # Очищаем таблицу
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        # Заполняем таблицу
        products = self.repository.get_products()
        for product in products:
            info = product.get_info()
            self.products_tree.insert('', tk.END, values=(
                info['product_id'],
                info['name'],
                f"{info['price']:.2f} ₽",
                info['category'],
                info['stock']
            ))

    def refresh_orders(self) -> None:
        """Обновить список заказов."""
        # Очищаем таблицу
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        # Заполняем таблицу
        orders = self.repository.get_orders()
        for order in orders:
            info = order.get_info()
            self.orders_tree.insert('', tk.END, values=(
                info['order_id'],
                info['customer_name'],
                info['order_date'][:10],  # Только дата без времени
                info['status'],
                info['items_count'],
                f"{info['total']:.2f} ₽"
            ))

    def refresh_all_data(self) -> None:
        """Обновить все данные в интерфейсе."""
        self.refresh_customers()
        self.refresh_products()
        self.refresh_orders()
        self.update_customer_combo()
        self.update_product_combo()
        self.update_statistics()

    def update_customer_combo(self) -> None:
        """Обновить список клиентов в комбобоксе."""
        customers = self.repository.get_customers()
        values = [f"{c.customer_id}: {c.name}" for c in customers]
        self.customer_combo['values'] = values

    def update_product_combo(self) -> None:
        """Обновить список товаров в комбобоксе."""
        products = self.repository.get_products()
        values = [f"{p.product_id}: {p.name} ({p.price}₽)" for p in products]
        self.product_combo['values'] = values

    def export_data(self) -> None:
        """Экспорт данных в файл."""
        try:
            directory = filedialog.askdirectory(title="Выберите папку для экспорта")
            if directory:
                if self.repository.export_data('csv', directory):
                    messagebox.showinfo("Успех", f"Данные успешно экспортированы в {directory}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось экспортировать данные")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

    def update_statistics(self) -> None:
        """Обновить статистику в текстовом поле."""
        try:
            customers = self.repository.get_customers()
            products = self.repository.get_products()
            orders = self.repository.get_orders()

            # Базовая статистика
            stats = f"=== ОБЩАЯ СТАТИСТИКА ===\n"
            stats += f"Клиентов в базе: {len(customers)}\n"
            stats += f"Товаров в каталоге: {len(products)}\n"
            stats += f"Заказов всего: {len(orders)}\n\n"

            if customers:
                # Статистика по клиентам
                total_spent = sum(c.get_total_spent() for c in customers)
                avg_spent = total_spent / len(customers) if customers else 0

                stats += f"=== КЛИЕНТЫ ===\n"
                stats += f"Общая сумма покупок: {total_spent:.2f} ₽\n"
                stats += f"Средние траты на клиента: {avg_spent:.2f} ₽\n"

                # Топ клиенты
                sorted_customers = sorted(customers, key=lambda x: x.get_total_spent(), reverse=True)
                stats += f"\nТоп 3 клиента по тратам:\n"
                for i, customer in enumerate(sorted_customers[:3], 1):
                    stats += f"{i}. {customer.name}: {customer.get_total_spent():.2f} ₽\n"

            if products:
                # Статистика по товарам
                stats += f"\n=== ТОВАРЫ ===\n"
                total_stock = sum(p.stock for p in products)
                stats += f"Общее количество на складе: {total_stock}\n"

                categories = {}
                for product in products:
                    cat = product.category or "Без категории"
                    categories[cat] = categories.get(cat, 0) + 1

                stats += f"\nКатегории товаров:\n"
                for cat, count in categories.items():
                    stats += f"- {cat}: {count} товар(ов)\n"

            if orders:
                # Статистика по заказам
                total_revenue = sum(o.get_total() for o in orders)
                avg_order = total_revenue / len(orders) if orders else 0

                stats += f"\n=== ЗАКАЗЫ ===\n"
                stats += f"Общая выручка: {total_revenue:.2f} ₽\n"
                stats += f"Средний чек: {avg_order:.2f} ₽\n"

                # Статусы заказов
                statuses = {}
                for order in orders:
                    statuses[order.status] = statuses.get(order.status, 0) + 1

                stats += f"\nСтатусы заказов:\n"
                for status, count in statuses.items():
                    stats += f"- {status}: {count}\n"

            # Обновляем текстовое поле
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats)

        except Exception as e:
            error_msg = f"Ошибка при обновлении статистики: {e}"
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, error_msg)

    def show_analytics_chart(self, chart_type: str) -> None:
        """Показать график аналитики."""
        try:
            customers = self.repository.get_customers()
            products = self.repository.get_products()
            orders = self.repository.get_orders()

            if not any([customers, products, orders]):
                messagebox.showwarning("Предупреждение", "Недостаточно данных для построения графиков")
                return

            # Создаем анализатор и генератор графиков
            analyzer = DataAnalyzer(customers, products, orders)
            chart_generator = ChartGenerator(analyzer)

            # Выбираем тип графика
            if chart_type == "top_customers_orders":
                chart_generator.plot_top_customers('orders', 5)
            elif chart_type == "top_customers_spending":
                chart_generator.plot_top_customers('spending', 5)
            elif chart_type == "sales_dynamics":
                chart_generator.plot_sales_dynamics('daily')
            elif chart_type == "product_sales":
                chart_generator.plot_product_sales_pie(8)
            elif chart_type == "city_distribution":
                chart_generator.plot_customer_city_distribution()
            elif chart_type == "customer_network":
                network_analyzer = NetworkAnalyzer(customers, orders)
                network_analyzer.plot_customer_network('product')

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графика: {e}")

    # Заглушки для остальных методов
    def import_data(self): pass
    def show_top_customers(self): pass
    def show_sales_dynamics(self): pass  
    def show_product_analysis(self): pass
    def show_network_analysis(self): pass
    def filter_customers(self): pass
    def update_stock(self): pass
    def add_item_to_order(self): pass
    def create_order(self): pass
    def clear_order_form(self): pass


def main():
    """Главная функция запуска приложения."""
    root = tk.Tk()
    app = ShopManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
