from django.core.management.base import BaseCommand

from faker import Faker

from internet_shop.models import Product
from internet_shop.models import Category
from internet_shop.models import Customer
from internet_shop.models import Order
from internet_shop.models import OrderDetail
import random
from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction


class Command(BaseCommand):
    help = 'Generate fake data for the internet shop'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1000,
            help='Number of records to create for each model (except categories)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        fake = Faker(['ru_RU'])
        
        self.stdout.write(f'Generating {count} records for each model (except categories)...')
        
        # Используем транзакцию для ускорения
        with transaction.atomic():
            # 1. Сначала создаем категории (фиксированное количество - 8)
            self.stdout.write('Creating categories...')
            categories = []
            category_names = [
                "Электроника", "Одежда", "Книги", "Дом и сад", 
                "Красота и здоровье", "Спорт", "Игрушки", "Автотовары"
            ]
            
            # Очищаем старые категории, если они есть
            Category.objects.all().delete()
            
            for cat_name in category_names:
                category = Category.objects.create(
                    name=cat_name,
                    description=fake.text(max_nb_chars=200)
                )
                categories.append(category)
                self.stdout.write(f'  Created: {cat_name}')
            
            # 2. Создаем продукты (count штук)
            self.stdout.write(f'Creating {count} products...')
            products = []
            product_base_names = [
                "Смартфон", "Ноутбук", "Наушники", "Футболка", "Джинсы",
                "Куртка", "Роман", "Учебник", "Диван", "Стол",
                "Стул", "Крем для лица", "Шампунь", "Мяч", "Велосипед",
                "Кукла", "Машинка", "Автомобильное масло", "Щетки стеклоочистителя",
                "Микроволновка", "Холодильник", "Телевизор", "Планшет", "Часы",
                "Обувь", "Платье", "Пиджак", "Рубашка", "Кофта", "Шорты",
                "Юбка", "Пальто", "Перчатки", "Шарф", "Шапка", "Рюкзак",
                "Сумка", "Косметичка", "Мыло", "Гель для душа", "Дезодорант",
                "Лак для волос", "Тени", "Помада", "Тушь", "Тонер", "Сыворотка",
                "Маска", "Скребок", "Монитор", "Клавиатура", "Мышь", "Колонки",
                "Настольная лампа", "Полка", "Шкаф", "Кровать", "Матрас", "Подушка",
                "Одеяло", "Простынь", "Полотенце", "Халат", "Зубная щетка", "Паста",
                "Расческа", "Зеркало", "Фен", "Плойка", "Утюг", "Пылесос",
                "Швабра", "Ведро", "Губка", "Моющее средство", "Кондиционер",
                "Порошок", "Отбеливатель", "Освежитель", "Свеча", "Картина",
                "Ваза", "Цветок", "Горшок", "Лейка", "Грабли", "Лопата",
                "Секатор", "Удобрение", "Корм", "Миска", "Ошейник", "Поводок",
                "Игрушка для кота", "Когтеточка", "Аквариум", "Корм для рыбок",
                "Наполнитель", "Переноска", "Вольер", "Будка", "Поилка"
            ]
            
            # Очищаем старые продукты
            Product.objects.all().delete()
            
            for i in range(count):
                base_name = random.choice(product_base_names)
                brand_or_model = fake.word().capitalize()
                color = random.choice(["черный", "белый", "синий", "красный", "зеленый", "желтый", "серый", "фиолетовый"])
                
                product = Product.objects.create(
                    name=f"{base_name} {brand_or_model} {color}",
                    price=Decimal(random.uniform(100, 50000)).quantize(Decimal('0.01')),
                    description=fake.text(max_nb_chars=300),
                    quantity=random.randint(0, 500),
                    category=random.choice(categories),
                )
                products.append(product)
                
                # Выводим прогресс каждые 100 товаров
                if (i + 1) % 100 == 0:
                    self.stdout.write(f'  Created {i + 1} products...')
            
            self.stdout.write(f'  ✅ Created {len(products)} products total')
            
            # 3. Создаем клиентов (count штук)
            self.stdout.write(f'Creating {count} customers...')
            customers = []
            
            # Очищаем старых клиентов
            Customer.objects.all().delete()
            
            for i in range(count):
                customer = Customer.objects.create(
                    name=fake.name(),
                    address=fake.address(),
                    phone_number=f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}",
                    email=fake.email(),
                )
                customers.append(customer)
                
                # Выводим прогресс каждые 100 клиентов
                if (i + 1) % 100 == 0:
                    self.stdout.write(f'  Created {i + 1} customers...')
            
            self.stdout.write(f'  ✅ Created {len(customers)} customers total')
            
            # 4. Создаем заказы (count * 2 штук - примерно по 2 заказа на клиента)
            self.stdout.write(f'Creating {count * 2} orders...')
            orders = []
            order_counter = 1
            
            # Очищаем старые заказы
            OrderDetail.objects.all().delete()
            Order.objects.all().delete()
            
            for i in range(count * 2):
                customer = random.choice(customers)
                order_date = fake.date_between(start_date='-365d', end_date='today')
                
                order = Order.objects.create(
                    order_number=order_counter,
                    date=order_date,
                    status=random.choice([
                        'В обработке', 'В сборке', 'Собран', 
                        'Отправлен', 'Доставлен', 'Отменен'
                    ]),
                    customer=customer
                )
                orders.append(order)
                order_counter += 1
                
                # 5. Создаем детали заказа для каждого заказа
                order_items_count = random.randint(1, 8)  # до 8 товаров в заказе
                for _ in range(order_items_count):
                    product = random.choice(products)
                    quantity = random.randint(1, 5)
                    OrderDetail.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity
                    )
                
                # Выводим прогресс каждые 200 заказов
                if (i + 1) % 200 == 0:
                    self.stdout.write(f'  Created {i + 1} orders...')
            
            self.stdout.write(f'  ✅ Created {len(orders)} orders total')
        
        # Вывод итоговой статистики
        total_products_in_stock = sum(p.quantity for p in Product.objects.all())
        total_order_details = OrderDetail.objects.count()
        unique_customers_with_orders = len(set(o.customer_id for o in Order.objects.all()))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully generated LARGE dataset:\n'
                f'   • Categories: {Category.objects.count()}\n'
                f'   • Products: {Product.objects.count():,}\n'
                f'   • Customers: {Customer.objects.count():,}\n'
                f'   • Orders: {Order.objects.count():,}\n'
                f'   • Order Details: {OrderDetail.objects.count():,}'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 Statistics:\n'
                f'   • Average products per order: {total_order_details / Order.objects.count():.1f}\n'
                f'   • Total products in stock: {total_products_in_stock:,}\n'
                f'   • Customers with orders: {unique_customers_with_orders:,}\n'
                f'   • Average orders per customer: {Order.objects.count() / Customer.objects.count():.1f}'
            )
        )