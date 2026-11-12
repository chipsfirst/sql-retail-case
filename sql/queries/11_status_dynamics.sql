-- Вопрос: как менялась доля отмен и возвратов по месяцам?
SELECT date_trunc('month', order_ts)::date AS month,
       COUNT(*) AS orders,
       ROUND(COUNT(*) FILTER (WHERE status = 'paid')::numeric / COUNT(*) * 100, 1)      AS paid_pct,
       ROUND(COUNT(*) FILTER (WHERE status = 'cancelled')::numeric / COUNT(*) * 100, 1) AS cancelled_pct,
       ROUND(COUNT(*) FILTER (WHERE status = 'refunded')::numeric / COUNT(*) * 100, 1)  AS refunded_pct
FROM orders
GROUP BY 1
ORDER BY 1;
