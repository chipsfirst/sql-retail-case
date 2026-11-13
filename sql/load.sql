-- Загрузка подготовленных CSV. Запускать из корня репозитория:
--   psql -U shop -d shop -v ON_ERROR_STOP=1 -f sql/load.sql
-- Файлы создаёт scripts/prepare_data.py из данных Kaggle.

\copy customers (customer_id, country, first_order_ts, last_order_ts, orders) FROM 'data/customers.csv' WITH (FORMAT csv, HEADER true)
\copy products (stock_code, description, min_price, max_price) FROM 'data/products.csv' WITH (FORMAT csv, HEADER true)
\copy orders (invoice_no, customer_id, invoice_ts, status, country) FROM 'data/orders.csv' WITH (FORMAT csv, HEADER true)
\copy order_items (invoice_no, stock_code, quantity, unit_price) FROM 'data/order_items.csv' WITH (FORMAT csv, HEADER true)

ANALYZE customers;
ANALYZE products;
ANALYZE orders;
ANALYZE order_items;
