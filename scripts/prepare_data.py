"""Подготовка датасета Online Retail II к загрузке в PostgreSQL.

Правила очистки (все решения зафиксированы и объяснены в README):

1. Оставляем только товарные позиции: StockCode вида 12345 или 12345A.
   Служебные строки (POST, DOT, BANK CHARGES, M, D) не товары.
2. Убираем строки с Price <= 0: бесплатные позиции, корректировки и ошибки.
3. Убираем нулевые количества.
4. Статус заказа: инвойс с префиксом C — отмена. В отменах количество отрицательное,
   поэтому выручка по ним отрицательная — это возврат денег.
5. Для оплаченных заказов оставляем только положительные количества.
6. Одинаковые пары (инвойс, товар) внутри заказа агрегируем: quantity = сумма,
   unit_price = выручка / количество (средневзвешенная цена).
7. Заказы без Customer ID сохраняем: это гостевые покупки, они нужны для выручки,
   но не участвуют в клиентских метриках.

Результат — четыре CSV в data/: customers, products, orders, order_items.
"""

import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
RAW = os.path.join(DATA, 'online_retail_II.csv')

PRODUCT_CODE = r'^\d{5}[A-Za-z]?$'

RAW_COLUMNS = ['Invoice', 'StockCode', 'Description', 'Quantity',
               'InvoiceDate', 'Price', 'Customer ID', 'Country']


def clean_frame(raw):
    """Применяет правила 1–5 и возвращает очищенный кадр с выручкой."""
    missing = [column for column in RAW_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(f'нет обязательных колонок: {missing}')

    frame = raw.copy()
    frame['StockCode'] = frame['StockCode'].astype(str)
    frame['Invoice'] = frame['Invoice'].astype(str)
    frame['InvoiceDate'] = pd.to_datetime(frame['InvoiceDate'])

    frame = frame[frame['StockCode'].str.match(PRODUCT_CODE)
                  & (frame['Price'] > 0)
                  & (frame['Quantity'] != 0)].copy()
    frame['status'] = frame['Invoice'].str.startswith('C').map(
        {True: 'cancelled', False: 'paid'})
    frame = frame[(frame['status'] == 'cancelled') | (frame['Quantity'] > 0)]
    frame['revenue'] = frame['Quantity'] * frame['Price']
    return frame


def build_tables(frame):
    """Собирает четыре таблицы для PostgreSQL из очищенного кадра."""
    grouped = (frame.groupby(['Invoice', 'StockCode', 'status'], as_index=False)
               .agg(quantity=('Quantity', 'sum'),
                    revenue=('revenue', 'sum'),
                    description=('Description', 'first'),
                    customer_id=('Customer ID', 'max'),
                    invoice_ts=('InvoiceDate', 'min'),
                    country=('Country', 'first')))
    grouped['unit_price'] = (grouped['revenue'] / grouped['quantity']).round(2)

    orders = (grouped.groupby('Invoice', as_index=False)
              .agg(customer_id=('customer_id', 'max'),
                   invoice_ts=('invoice_ts', 'min'),
                   status=('status', 'first'),
                   country=('country', 'first')))
    orders['invoice_ts'] = pd.to_datetime(orders['invoice_ts'])
    orders = orders.sort_values('invoice_ts')

    paid = orders[orders['status'] == 'paid']

    # Клиент существует, если встречается в любом инвойсе, включая отмены:
    # иначе заказы с отменёнными покупками нарушат внешний ключ.
    identified = orders.dropna(subset=['customer_id']).copy()
    identified['customer_id'] = identified['customer_id'].astype('int64')
    paid_counts = (paid.dropna(subset=['customer_id'])
                   .groupby('customer_id')['Invoice'].nunique())

    customers = (identified.groupby('customer_id', as_index=False)
                 .agg(country=('country', lambda s: s.mode().iat[0]),
                      first_order_ts=('invoice_ts', 'min'),
                      last_order_ts=('invoice_ts', 'max')))
    customers['orders'] = (customers['customer_id'].map(paid_counts)
                           .fillna(0).astype('int64'))

    products = (grouped.dropna(subset=['description'])
                .assign(description=lambda d: d['description'].astype(str).str.strip())
                .groupby('StockCode', as_index=False)
                .agg(description=('description', lambda s: s.mode().iat[0]),
                     min_price=('unit_price', 'min'),
                     max_price=('unit_price', 'max'))
                .rename(columns={'StockCode': 'stock_code'}))

    items = grouped[['Invoice', 'StockCode', 'quantity', 'unit_price']].rename(
        columns={'Invoice': 'invoice_no', 'StockCode': 'stock_code'})
    orders_out = orders.rename(columns={'Invoice': 'invoice_no'})[
        ['invoice_no', 'customer_id', 'invoice_ts', 'status', 'country']]

    orders_out['invoice_ts'] = orders_out['invoice_ts'].dt.strftime('%Y-%m-%d %H:%M:%S')
    customers['first_order_ts'] = customers['first_order_ts'].dt.strftime('%Y-%m-%d %H:%M:%S')
    customers['last_order_ts'] = customers['last_order_ts'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return {
        'orders': orders_out,
        'order_items': items,
        'customers': customers,
        'products': products,
    }


def write_tables(tables, data_dir):
    for name, table in tables.items():
        table.to_csv(os.path.join(data_dir, f'{name}.csv'), index=False)


def main():
    raw = pd.read_csv(RAW, dtype={'Customer ID': 'Int64'})
    print(f'исходных строк: {len(raw):,}')

    frame = clean_frame(raw)
    print(f'после фильтра товаров, цен и количеств: {len(frame):,}')

    tables = build_tables(frame)
    print(f'после агрегации строк заказа: {len(tables["order_items"]):,}')
    write_tables(tables, DATA)

    revenue = (frame.loc[frame['status'] == 'paid', 'revenue'].sum())
    paid_orders = int((tables['orders']['status'] == 'paid').sum())
    print(f'заказов: {len(tables["orders"]):,} (оплаченных {paid_orders:,})')
    print(f'позиций: {len(tables["order_items"]):,}')
    print(f'клиентов с ID: {len(tables["customers"]):,}')
    print(f'товаров: {len(tables["products"]):,}')
    print(f'выручка по оплаченным заказам: {revenue:,.2f}')


if __name__ == '__main__':
    main()
