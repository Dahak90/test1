#!/usr/bin/env python3
import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback
from datetime import datetime
import sqlite3

# Добавляем текущую директорию в path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from models import Customer, Product, Order
    from db import DataRepository
    from gui import ShopManagerGUI
    from analysis import DataAnalyzer
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все модули находятся в одной директории")
    sys.exit(1)


def create_sample_data(repository: DataRepository) -> None:
    try:
        print("Создание образцов данных...")

        # Создание клиентов
        customers_data = [
            (1, "Иван Петров", "ivan.petrov@email.com", "+7(495)123-45-67", "ул. Тверская, 10", "Москва"),
            (2, "Мария Сидорова", "maria.sidorova@email.com", "+7(812)987-65-43", "Невский пр., 25", "Санкт-Петербург"),
            (3, "Алексей Козлов", "alexey.kozlov@email.com", "+7(383)555-12-34", "ул. Ленина, 15", "Новосибирск"),
            (4, "Елена Васильева", "elena.vasileva@email.com", "+7(843)777-88-99", "ул. Баумана, 5", "Казань"),
            (5, "Дмитрий Николаев", "dmitry.nikolaev@email.com", "+7(495)456-78-90", "ул. Арбат, 3", "Москва"),
        ]

        customers = []
        for customer_data in customers_data:
            customer = Customer(*customer_data)
            if repository.add_customer(customer):
                customers.append(customer)
                print(f"Добавлен клиент: {customer.name}")

        # Создание товаров
        products_data = [
            (1, "Ноутбук ASUS ROG", 85000.0, "Компьютеры", "Игровой ноутбук 15.6\"", 5),
            (2, "Смартфон iPhone 13", 65000.0, "Телефоны", "128GB, синий", 10),
            (3, "Наушники Sony WH-1000XM4", 25000.0, "Аудио", "Беспроводные с шумоподавлением", 15),
            (4, "Клавиатура Logitech MX Keys", 8500.0, "Аксессуары", "Беспроводная механическая", 20),
            (5, "Мышь Logitech MX Master 3", 6500.0, "Аксессуары", "Беспроводная эргономичная", 25),
            (6, "Монитор Dell UltraSharp", 35000.0, "Мониторы", "27\" 4K IPS", 8),
            (7, "SSD Samsung 980 PRO", 12000.0, "Комплектующие", "1TB NVMe M.2", 30),
            (8, "Веб-камера Logitech C920", 7500.0, "Аксессуары", "Full HD 1080p", 12),
        ]

        products = []
        for product_data in products_data:
            product = Product(*product_data)
            if repository.add_product(product):
                products.append(product)
                print(f"Добавлен товар: {product.name}")

        # Создание заказов
        if customers and products:
            from datetime import datetime, timedelta
            import random

            order_id = 1
            for i, customer in enumerate(customers):
                # Создаем 1-3 заказа для каждого клиента
                num_orders = random.randint(1, 3)

                for j in range(num_orders):
                    # Создаем заказ с датой в последние 30 дней
                    order_date = datetime.now() - timedelta(days=random.randint(0, 30))
                    order = Order(order_id, customer, order_date)

                    # Добавляем 1-4 товара в заказ
                    num_items = random.randint(1, 4)
                    selected_products = random.sample(products, min(num_items, len(products)))

                    for product in selected_products:
                        quantity = random.randint(1, 3)
                        if product.is_available(quantity):
                            order.add_item(product, quantity)
                            # Обновляем склад
                            product.update_stock(-quantity)

                    # Устанавливаем статус заказа
                    statuses = ["Новый", "В обработке", "Отправлен", "Доставлен", "Завершен"]
                    order.status = random.choice(statuses)

                    if repository.add_order(order):
                        print(f"Добавлен заказ #{order_id} для {customer.name}")

                    order_id += 1

        print("Образцы данных успешно созданы!")

    except Exception as e:
        print(f"Ошибка при создании образцов данных: {e}")
        traceback.print_exc()


def check_dependencies() -> bool:
    required_modules = [
        'tkinter',
        'sqlite3', 
        'pandas',
        'matplotlib',
        'seaborn',
        'networkx',
        'numpy'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("Отсутствуют следующие модули:")
        for module in missing_modules:
            print(f"- {module}")
        print("\nУстановите их с помощью pip:")
        print(f"pip install {' '.join(missing_modules)}")
        return False

    return True


def setup_logging() -> None:
    """Настроить логирование приложения."""
    import logging

    # Создаем директорию для логов
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Настраиваем логирование
    log_filename = os.path.join(log_dir, f"shop_manager_{datetime.now().strftime('%Y%m%d')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Запуск приложения 'Менеджер интернет-магазина'")
    return logger


def initialize_database() -> bool:
    try:
        # Создаем директорию для данных
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Путь к базе данных
        db_path = os.path.join(data_dir, "shop_database.db")

        # Тестируем соединение
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()

        print(f"База данных инициализирована: {db_path}")
        return True

    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}")
        return False


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = f"Произошла критическая ошибка:\n\n{exc_type.__name__}: {exc_value}"

    print("="*50)
    print("КРИТИЧЕСКАЯ ОШИБКА")
    print("="*50)
    traceback.print_exception(exc_type, exc_value, exc_traceback)

    # Показываем сообщение пользователю, если возможно
    try:
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        messagebox.showerror("Критическая ошибка", error_msg + "\n\nПриложение будет закрыто.")
        root.destroy()
    except:
        pass


def main():
    """
    Главная функция приложения.
    """
    print("="*60)
    print("МЕНЕДЖЕР ИНТЕРНЕТ-МАГАЗИНА")
    print("="*60)
    print("Запуск приложения...")

    try:
        # Устанавливаем обработчик исключений
        sys.excepthook = handle_exception

        # Настраиваем логирование
        logger = setup_logging()

        # Проверяем зависимости
        if not check_dependencies():
            print("\nНе удалось запустить приложение из-за отсутствующих зависимостей.")
            sys.exit(1)

        # Инициализируем базу данных
        if not initialize_database():
            print("\nНе удалось инициализировать базу данных.")
            sys.exit(1)

        # Создаем репозиторий данных
        repository = DataRepository(use_database=True)

        # Проверяем, есть ли данные в базе
        customers = repository.get_customers()
        products = repository.get_products()
        orders = repository.get_orders()

        # Если базы пуста, создаем образцы данных
        if not customers and not products and not orders:
            print("\nБаза данных пуста. Создание образцов данных...")
            try:
                create_sample_data(repository)
                repository.load_all_data()  # Перезагружаем данные
                print("Образцы данных успешно загружены!")
            except Exception as e:
                print(f"Предупреждение: Не удалось создать образцы данных: {e}")

        # Запускаем GUI
        print("\nЗапуск графического интерфейса...")
        root = tk.Tk()

        # Настройки главного окна
        root.title("Менеджер интернет-магазина")
        root.geometry("1200x800")
        root.minsize(800, 600)

        # Устанавливаем иконку (если есть)
        try:
            # Можно добавить иконку приложения
            # root.iconbitmap('icon.ico')
            pass
        except:
            pass

        # Создаем и запускаем приложение
        app = ShopManagerGUI(root)

        logger.info("GUI успешно инициализирован")
        print("Приложение готово к работе!")
        print("="*60)

        # Запускаем главный цикл
        root.mainloop()

        logger.info("Приложение завершено пользователем")

    except KeyboardInterrupt:
        print("\n\nПриложение остановлено пользователем (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\nФатальная ошибка при запуске приложения: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
