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


def main():
    raw = pd.read_csv(RAW, dtype={'Customer ID': 'Int64'})
    raw['StockCode'] = raw['StockCode'].astype(str)
    raw['Invoice'] = raw['Invoice'].astype(str)
    print(f'исходных строк: {len(raw):,}')

    frame = raw[raw['StockCode'].str.match(PRODUCT_CODE)
                & (raw['Price'] > 0)
                & (raw['Quantity'] != 0)].copy()
    frame['status'] = frame['Invoice'].str.startswith('C').map({True: 'cancelled', False: 'paid'})
    frame = frame[(frame['status'] == 'cancelled') | (frame['Quantity'] > 0)]
    print(f'после фильтра товаров, цен и количеств: {len(frame):,}')

    frame['revenue'] = frame['Quantity'] * frame['Price']
    grouped = (frame.groupby(['Invoice', 'StockCode', 'status'], as_index=False)
               .agg(quantity=('Quantity', 'sum'),
                    revenue=('revenue', 'sum'),
                    description=('Description', 'first'),
                    customer_id=('Customer ID', 'max'),
                    invoice_ts=('InvoiceDate', 'min'),
                    country=('Country', 'first')))
    grouped['unit_price'] = (grouped['revenue'] / grouped['quantity']).round(2)
    print(f'после агрегации строк заказа: {len(grouped):,}')

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

    orders_out.to_csv(os.path.join(DATA, 'orders.csv'), index=False)
    items.to_csv(os.path.join(DATA, 'order_items.csv'), index=False)
    customers.to_csv(os.path.join(DATA, 'customers.csv'), index=False)
    products.to_csv(os.path.join(DATA, 'products.csv'), index=False)

    revenue = (grouped.loc[grouped['status'] == 'paid', 'revenue'].sum())
    print(f'заказов: {len(orders_out):,} (оплаченных {len(paid):,})')
    print(f'позиций: {len(items):,}')
    print(f'клиентов с ID: {len(customers):,}')
    print(f'товаров: {len(products):,}')
    print(f'выручка по оплаченным заказам: {revenue:,.2f}')


if __name__ == '__main__':
    main()
