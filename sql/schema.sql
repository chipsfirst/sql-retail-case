-- Схема интернет-магазина: 4 таблицы и одно представление.
-- Запуск: psql -U shop -d shop -f sql/schema.sql

DROP VIEW IF EXISTS v_paid_order_totals;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id  integer PRIMARY KEY,
    signup_date  date        NOT NULL,
    city         text        NOT NULL,
    channel      text        NOT NULL CHECK (channel IN ('organic', 'ads', 'referral', 'email')),
    age_group    text        NOT NULL
);

CREATE TABLE products (
    product_id  integer PRIMARY KEY,
    name        text         NOT NULL,
    category    text         NOT NULL,
    list_price  numeric(10, 2) NOT NULL CHECK (list_price > 0)
);

CREATE TABLE orders (
    order_id     integer PRIMARY KEY,
    customer_id  integer NOT NULL REFERENCES customers (customer_id),
    order_ts     timestamp NOT NULL,
    status       text      NOT NULL CHECK (status IN ('paid', 'cancelled', 'refunded')),
    channel      text      NOT NULL CHECK (channel IN ('organic', 'ads', 'referral', 'email'))
);

CREATE TABLE order_items (
    order_id    integer  NOT NULL REFERENCES orders (order_id) ON DELETE CASCADE,
    product_id  integer  NOT NULL REFERENCES products (product_id),
    quantity    smallint NOT NULL CHECK (quantity > 0),
    unit_price  numeric(10, 2) NOT NULL CHECK (unit_price > 0),
    discount    numeric(4, 2)  NOT NULL DEFAULT 0 CHECK (discount BETWEEN 0 AND 0.9),
    PRIMARY KEY (order_id, product_id)
);

CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_ts       ON orders (order_ts);
CREATE INDEX idx_orders_status   ON orders (status);
CREATE INDEX idx_items_product   ON order_items (product_id);

-- Выручка считается только по оплаченным заказам:
-- отменённые и возвращённые заказы в деньги не попадают.
CREATE VIEW v_paid_order_totals AS
SELECT o.order_id,
       o.customer_id,
       o.order_ts,
       o.channel,
       SUM(i.quantity * i.unit_price * (1 - i.discount))::numeric(12, 2) AS revenue,
       SUM(i.quantity)                                                   AS tickets
FROM orders o
JOIN order_items i USING (order_id)
WHERE o.status = 'paid'
GROUP BY o.order_id, o.customer_id, o.order_ts, o.channel;
