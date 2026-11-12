"""Генератор синтетических данных интернет-магазина.

Детерминированный (seed=42): при повторном запуске получаются те же файлы.
Пишет четыре CSV в data/: customers, products, orders, order_items.

Только стандартная библиотека Python, внешние зависимости не нужны.
"""

import csv
import os
import random
from datetime import date, datetime, timedelta

SEED = 42
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

START = date(2024, 1, 1)
END = date(2025, 12, 31)
SIGNUP_START = date(2023, 6, 1)
N_CUSTOMERS = 8000
N_PRODUCTS = 300

CITIES = ['Москва', 'Санкт-Петербург', 'Казань', 'Новосибирск', 'Екатеринбург',
          'Нижний Новгород', 'Самара', 'Краснодар', 'Воронеж', 'Пермь']
CITY_WEIGHTS = [0.30, 0.16, 0.09, 0.08, 0.08, 0.07, 0.07, 0.07, 0.04, 0.04]

CHANNELS = ['organic', 'ads', 'referral', 'email']
CHANNEL_WEIGHTS = [0.40, 0.30, 0.15, 0.15]
# базовая месячная вероятность покупки по каналу привлечения
CHANNEL_ACTIVITY = {'organic': 0.11, 'ads': 0.17, 'referral': 0.14, 'email': 0.15}

AGE_GROUPS = ['18-24', '25-34', '35-44', '45-54', '55+']
AGE_WEIGHTS = [0.18, 0.34, 0.26, 0.14, 0.08]

SEASONALITY = {1: 0.90, 2: 0.85, 3: 0.95, 4: 0.95, 5: 1.00, 6: 0.95,
               7: 0.90, 8: 0.90, 9: 1.00, 10: 1.05, 11: 1.15, 12: 1.30}

CATEGORIES = {
    'Электроника': {
        'price': (1900, 42000), 'popularity': 0.25,
        'nouns': ['Наушники', 'Планшет', 'Клавиатура', 'Мышь', 'Колонка', 'Монитор', 'Роутер', 'Фитнес-браслет'],
        'brands': ['Aurora', 'Nexa', 'Volt', 'Kite', 'Orbis', 'Delta'],
    },
    'Дом и кухня': {
        'price': (450, 13000), 'popularity': 0.18,
        'nouns': ['Чайник', 'Сковорода', 'Кофемолка', 'Плед', 'Лампа', 'Органайзер', 'Термос'],
        'brands': ['Homey', 'Tepla', 'Nord', 'Sova', 'Brik'],
    },
    'Одежда': {
        'price': (800, 9500), 'popularity': 0.20,
        'nouns': ['Куртка', 'Футболка', 'Джинсы', 'Свитер', 'Плащ', 'Кроссовки', 'Шарф'],
        'brands': ['Linea', 'Sever', 'Mono', 'Ruta', 'Kedr'],
    },
    'Спорт': {
        'price': (700, 16000), 'popularity': 0.10,
        'nouns': ['Коврик', 'Гантель', 'Скакалка', 'Рюкзак', 'Бутылка', 'Эспандер'],
        'brands': ['Sporto', 'Titan', 'Runa', 'Aktiv'],
    },
    'Красота': {
        'price': (300, 6500), 'popularity': 0.08,
        'nouns': ['Крем', 'Шампунь', 'Сыворотка', 'Набор кистей', 'Парфюм', 'Маска'],
        'brands': ['Lumi', 'Aura', 'Botanika', 'Vera'],
    },
    'Книги': {
        'price': (300, 2600), 'popularity': 0.07,
        'nouns': ['Роман', 'Сборник рассказов', 'Атлас', 'Учебник', 'Комикс', 'Путеводитель'],
        'brands': ['Slovo', 'Pegas', 'List', 'Kvant'],
    },
    'Игры': {
        'price': (500, 8500), 'popularity': 0.07,
        'nouns': ['Настольная игра', 'Пазл', 'Конструктор', 'Карточная игра', 'Кубики'],
        'brands': ['Playbox', 'Kubik', 'Riddle', 'Lair'],
    },
    'Зоотовары': {
        'price': (200, 4500), 'popularity': 0.05,
        'nouns': ['Корм', 'Лежанка', 'Игрушка', 'Поводок', 'Переноска', 'Наполнитель'],
        'brands': ['Zoo', 'Kotik', 'Paw', 'Barsik'],
    },
}


def month_iter(start, end):
    current = date(start.year, start.month, 1)
    while current <= end:
        yield current
        current = date(current.year + (current.month == 12), (current.month % 12) + 1, 1)


def build_products(rng):
    products = []
    categories = list(CATEGORIES.items())
    product_id = 1
    while len(products) < N_PRODUCTS:
        for category, meta in categories:
            if len(products) >= N_PRODUCTS:
                break
            noun = rng.choice(meta['nouns'])
            brand = rng.choice(meta['brands'])
            low, high = meta['price']
            price = round(rng.uniform(low, high), -1) + rng.choice([0, 99])
            products.append({
                'product_id': product_id,
                'name': f'{noun} {brand} {rng.randint(1, 9)}',
                'category': category,
                'list_price': max(price, low),
            })
            product_id += 1
    return products


def build_customers(rng):
    customers = []
    span = (END - SIGNUP_START).days
    for customer_id in range(1, N_CUSTOMERS + 1):
        signup = SIGNUP_START + timedelta(days=rng.randint(0, span))
        customers.append({
            'customer_id': customer_id,
            'signup_date': signup.isoformat(),
            'city': rng.choices(CITIES, CITY_WEIGHTS)[0],
            'channel': rng.choices(CHANNELS, CHANNEL_WEIGHTS)[0],
            'age_group': rng.choices(AGE_GROUPS, AGE_WEIGHTS)[0],
        })
    return customers


def build_orders(rng, customers, products):
    products_by_category = {}
    for product in products:
        products_by_category.setdefault(product['category'], []).append(product)
    category_names = list(products_by_category)
    category_weights = [CATEGORIES[name]['popularity'] for name in category_names]

    orders, items = [], []
    order_id = 1
    for customer in customers:
        signup = date.fromisoformat(customer['signup_date'])
        first_month = max(signup, START)
        activity = CHANNEL_ACTIVITY[customer['channel']]
        if rng.random() < 0.05:          # небольшая доля активных покупателей
            activity *= 2.5
        months_seen = 0
        for month_start in month_iter(first_month, END):
            decay = 0.97 ** months_seen
            probability = activity * decay * SEASONALITY[month_start.month]
            months_seen += 1
            if rng.random() >= probability:
                continue

            days_in_month = ((date(month_start.year + (month_start.month == 12),
                                   (month_start.month % 12) + 1, 1)) - month_start).days
            order_day = month_start + timedelta(days=rng.randint(0, days_in_month - 1))
            order_ts = datetime.combine(order_day, datetime.min.time()) + timedelta(
                hours=rng.randint(8, 22), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59))
            status = rng.choices(['paid', 'cancelled', 'refunded'], [0.93, 0.05, 0.02])[0]

            orders.append({
                'order_id': order_id,
                'customer_id': customer['customer_id'],
                'order_ts': order_ts.strftime('%Y-%m-%d %H:%M:%S'),
                'status': status,
                'channel': customer['channel'],
            })

            n_items = rng.choices([1, 2, 3, 4, 5], [0.40, 0.30, 0.15, 0.10, 0.05])[0]
            chosen = set()
            for _ in range(n_items):
                category = rng.choices(category_names, category_weights)[0]
                product = rng.choice(products_by_category[category])
                if product['product_id'] in chosen:
                    continue
                chosen.add(product['product_id'])
                quantity = rng.choices([1, 2, 3], [0.72, 0.20, 0.08])[0]
                price = round(product['list_price'] * rng.uniform(0.95, 1.05), 2)
                promo = month_start.month in (11, 12)
                if rng.random() < (0.45 if promo else 0.30):
                    discount = rng.choice([0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
                else:
                    discount = 0
                items.append({
                    'order_id': order_id,
                    'product_id': product['product_id'],
                    'quantity': quantity,
                    'unit_price': price,
                    'discount': discount,
                })
            order_id += 1
    return orders, items


def write_csv(name, rows, fields):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f'{path}: {len(rows):,} строк')


def main():
    rng = random.Random(SEED)
    products = build_products(rng)
    customers = build_customers(rng)
    orders, items = build_orders(rng, customers, products)

    write_csv('products.csv', products, ['product_id', 'name', 'category', 'list_price'])
    write_csv('customers.csv', customers, ['customer_id', 'signup_date', 'city', 'channel', 'age_group'])
    write_csv('orders.csv', orders, ['order_id', 'customer_id', 'order_ts', 'status', 'channel'])
    write_csv('order_items.csv', items, ['order_id', 'product_id', 'quantity', 'unit_price', 'discount'])


if __name__ == '__main__':
    main()
