-- Вопрос: какие страны дают выручку и сколько приходится на заказ?
WITH by_country AS (
    SELECT country,
           SUM(revenue)      AS revenue,
           COUNT(*)          AS orders,
           COUNT(DISTINCT customer_id) AS customers
    FROM v_paid_order_totals
    GROUP BY country
)
SELECT country,
       revenue,
       orders,
       customers,
       ROUND(revenue / SUM(revenue) OVER () * 100, 2) AS revenue_share_pct,
       ROUND(revenue / orders, 2)                     AS revenue_per_order
FROM by_country
ORDER BY revenue DESC
LIMIT 10;
