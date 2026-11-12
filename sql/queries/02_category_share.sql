-- Вопрос: какие категории дают выручку и сколько приходится на заказ?
WITH by_category AS (
    SELECT p.category,
           SUM(i.quantity * i.unit_price * (1 - i.discount)) AS revenue,
           COUNT(DISTINCT o.order_id)                        AS orders
    FROM order_items i
    JOIN orders o   USING (order_id)
    JOIN products p USING (product_id)
    WHERE o.status = 'paid'
    GROUP BY p.category
)
SELECT category,
       revenue,
       orders,
       ROUND(revenue / SUM(revenue) OVER () * 100, 1) AS revenue_share_pct,
       ROUND(revenue / orders, 2)                     AS revenue_per_order
FROM by_category
ORDER BY revenue DESC;
