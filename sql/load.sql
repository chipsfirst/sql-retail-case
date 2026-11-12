-- Загрузка данных из CSV. Запускать из корня репозитория:
--   psql -U shop -d shop -v ON_ERROR_STOP=1 -f sql/load.sql
-- Файлы создаёт scripts/generate_data.py.

\copy customers (customer_id, signup_date, city, channel, age_group) FROM 'data/customers.csv' WITH (FORMAT csv, HEADER true)
\copy products (product_id, name, category, list_price) FROM 'data/products.csv' WITH (FORMAT csv, HEADER true)
\copy orders (order_id, customer_id, order_ts, status, channel) FROM 'data/orders.csv' WITH (FORMAT csv, HEADER true)
\copy order_items (order_id, product_id, quantity, unit_price, discount) FROM 'data/order_items.csv' WITH (FORMAT csv, HEADER true)

ANALYZE customers;
ANALYZE products;
ANALYZE orders;
ANALYZE order_items;
