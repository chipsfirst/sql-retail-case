-- Вопрос: как долго живут клиенты от первой до последней покупки?
WITH spans AS (
    SELECT customer_id,
           MIN(order_ts)::date AS first_order,
           MAX(order_ts)::date AS last_order,
           COUNT(*)            AS orders
    FROM v_paid_order_totals
    GROUP BY 1
)
SELECT CASE
           WHEN orders = 1 THEN '1 заказ'
           WHEN last_order - first_order <= 30 THEN '2+ заказа, до 30 дней'
           WHEN last_order - first_order <= 180 THEN '2+ заказа, 31–180 дней'
           ELSE '2+ заказа, больше 180 дней'
       END AS segment,
       COUNT(*)                                        AS customers,
       ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) AS share_pct,
       ROUND(AVG(last_order - first_order), 1)         AS avg_span_days,
       ROUND(AVG(orders), 2)                           AS avg_orders
FROM spans
GROUP BY 1
ORDER BY customers DESC;
