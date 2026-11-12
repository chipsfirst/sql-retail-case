-- Вопрос: как размер скидки связан со средним чеком и выручкой?
WITH order_discount AS (
    SELECT o.order_id,
           SUM(i.quantity * i.unit_price)                  AS gross,
           SUM(i.quantity * i.unit_price * (1 - i.discount)) AS net
    FROM orders o
    JOIN order_items i USING (order_id)
    WHERE o.status = 'paid'
    GROUP BY 1
)
SELECT CASE
           WHEN net = gross THEN '0%'
           WHEN 1 - net / gross <= 0.10 THEN '1–10%'
           WHEN 1 - net / gross <= 0.20 THEN '10–20%'
           ELSE '20%+'
       END AS discount_bucket,
       COUNT(*)              AS orders,
       ROUND(SUM(net), 2)    AS revenue,
       ROUND(AVG(net), 2)    AS avg_check,
       ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) AS orders_share_pct
FROM order_discount
GROUP BY 1
ORDER BY 1;
