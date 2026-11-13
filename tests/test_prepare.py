import pandas as pd
import pytest

from scripts.prepare_data import build_tables, clean_frame


def raw_frame():
    return pd.DataFrame([
        # оплаченный заказ, две строки одного товара — должны агрегироваться
        {'Invoice': '1001', 'StockCode': '12345', 'Description': 'Widget A', 'Quantity': 2,
         'InvoiceDate': '2010-01-05 10:00:00', 'Price': 10.0, 'Customer ID': 1, 'Country': 'United Kingdom'},
        {'Invoice': '1001', 'StockCode': '12345', 'Description': 'Widget A', 'Quantity': 1,
         'InvoiceDate': '2010-01-05 10:00:00', 'Price': 10.0, 'Customer ID': 1, 'Country': 'United Kingdom'},
        # нулевая цена — отбрасывается
        {'Invoice': '1002', 'StockCode': '12345', 'Description': 'Widget A', 'Quantity': 1,
         'InvoiceDate': '2010-01-06 10:00:00', 'Price': 0.0, 'Customer ID': 1, 'Country': 'United Kingdom'},
        # служебный код — отбрасывается
        {'Invoice': '1003', 'StockCode': 'POST', 'Description': 'Postage', 'Quantity': 1,
         'InvoiceDate': '2010-01-07 10:00:00', 'Price': 10.0, 'Customer ID': 1, 'Country': 'United Kingdom'},
        # нулевое количество — отбрасывается
        {'Invoice': '1004', 'StockCode': '12345', 'Description': 'Widget A', 'Quantity': 0,
         'InvoiceDate': '2010-01-08 10:00:00', 'Price': 10.0, 'Customer ID': 1, 'Country': 'United Kingdom'},
        # отмена для клиента 2
        {'Invoice': 'C1005', 'StockCode': '12345', 'Description': 'Widget A', 'Quantity': -2,
         'InvoiceDate': '2010-02-01 10:00:00', 'Price': 10.0, 'Customer ID': 2, 'Country': 'Germany'},
        # гостевой оплаченный заказ
        {'Invoice': '1006', 'StockCode': '12346', 'Description': 'Widget B', 'Quantity': 3,
         'InvoiceDate': '2010-02-10 10:00:00', 'Price': 5.0, 'Customer ID': pd.NA, 'Country': 'United Kingdom'},
    ])


def test_clean_frame_applies_rules():
    cleaned = clean_frame(raw_frame())
    assert len(cleaned) == 4
    assert set(cleaned['Invoice']) == {'1001', 'C1005', '1006'}
    assert cleaned.loc[cleaned['Invoice'] == 'C1005', 'status'].iat[0] == 'cancelled'
    assert cleaned.loc[cleaned['Invoice'] == '1001', 'status'].iat[0] == 'paid'
    assert cleaned['revenue'].sum() == pytest.approx(2 * 10 + 1 * 10 + (-2) * 10 + 3 * 5)


def test_clean_frame_requires_columns():
    with pytest.raises(ValueError):
        clean_frame(pd.DataFrame({'Invoice': ['1']}))


def test_build_tables_aggregates_duplicates():
    tables = build_tables(clean_frame(raw_frame()))
    items = tables['order_items'].set_index(['invoice_no', 'stock_code'])
    assert items.loc[('1001', '12345'), 'quantity'] == 3
    assert items.loc[('1001', '12345'), 'unit_price'] == pytest.approx(10.0)


def test_build_tables_orders_and_customers():
    tables = build_tables(clean_frame(raw_frame()))
    orders = tables['orders']

    assert len(orders) == 3
    assert (orders['status'] == 'paid').sum() == 2
    assert orders.loc[orders['invoice_no'] == '1006', 'customer_id'].isna().all()

    customers = tables['customers'].set_index('customer_id')
    assert set(customers.index) == {1, 2}
    assert customers.loc[1, 'orders'] == 1
    assert customers.loc[2, 'orders'] == 0   # у клиента 2 только отмена


def test_products_table():
    tables = build_tables(clean_frame(raw_frame()))
    products = tables['products'].set_index('stock_code')
    assert set(products.index) == {'12345', '12346'}
    assert products.loc['12346', 'description'] == 'Widget B'
