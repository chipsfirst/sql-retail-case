-- Схема интернет-магазина по данным Online Retail II.
-- Запуск: psql -U shop -d shop -f sql/schema.sql

DROP VIEW IF EXISTS v_paid_order_totals;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id    bigint PRIMARY KEY,
    country        text NOT NULL,
    first_order_ts timestamp NOT NULL,
    last_order_ts  timestamp NOT NULL,
    orders         integer NOT NULL
);

CREATE TABLE products (
    stock_code  text PRIMARY KEY,
    description text NOT NULL,
    min_price   numeric(10, 2) NOT NULL,
    max_price   numeric(10, 2) NOT NULL
);

CREATE TABLE orders (
    invoice_no  text PRIMARY KEY,
    customer_id bigint REFERENCES customers (customer_id),
    invoice_ts  timestamp NOT NULL,
    status      text NOT NULL CHECK (status IN ('paid', 'cancelled')),
    country     text NOT NULL
);

CREATE TABLE order_items (
    invoice_no text         NOT NULL REFERENCES orders (invoice_no) ON DELETE CASCADE,
    stock_code text         NOT NULL REFERENCES products (stock_code),
    quantity   integer      NOT NULL,
    unit_price numeric(10, 2) NOT NULL,
    PRIMARY KEY (invoice_no, stock_code)
);

CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_ts       ON orders (invoice_ts);
CREATE INDEX idx_orders_status   ON orders (status);
CREATE INDEX idx_items_product   ON order_items (stock_code);

-- Выручка по оплаченным заказам. Отмены (префикс C) исключены:
-- их отрицательные количества компенсируют исходные продажи.
CREATE VIEW v_paid_order_totals AS
SELECT o.invoice_no,
       o.customer_id,
       o.invoice_ts,
       o.country,
       SUM(i.quantity * i.unit_price)::numeric(12, 2) AS revenue,
       SUM(i.quantity)                               AS units
FROM orders o
JOIN order_items i USING (invoice_no)
WHERE o.status = 'paid'
GROUP BY o.invoice_no, o.customer_id, o.invoice_ts, o.country;
