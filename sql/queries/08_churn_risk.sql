-- Вопрос: сколько клиентов не покупали 90 дней и сколько денег с ними связано?
WITH bounds AS (
    SELECT MAX(order_ts)::date AS max_date FROM v_paid_order_totals
),
last_order AS (
    SELECT customer_id,
           MAX(order_ts)::date AS last_date,
           COUNT(*)            AS orders,
           SUM(revenue)        AS lifetime_revenue
    FROM v_paid_order_totals
    GROUP BY 1
)
SELECT COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE last_date <= (SELECT max_date FROM bounds) - 90) AS inactive_90d,
       ROUND(COUNT(*) FILTER (WHERE last_date <= (SELECT max_date FROM bounds) - 90)::numeric
             / COUNT(*) * 100, 1) AS inactive_share_pct,
       ROUND(SUM(lifetime_revenue) FILTER (WHERE last_date <= (SELECT max_date FROM bounds) - 90), 2)
             AS revenue_at_risk
FROM last_order;
