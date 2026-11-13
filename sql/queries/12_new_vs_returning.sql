-- Вопрос: чем растёт активная аудитория — новыми клиентами или возвратами?
WITH first_paid AS (
    SELECT customer_id, MIN(invoice_ts) AS first_ts
    FROM v_paid_order_totals
    WHERE customer_id IS NOT NULL
    GROUP BY 1
),
monthly AS (
    SELECT date_trunc('month', t.invoice_ts)::date AS month,
           COUNT(*)                               AS orders,
           COUNT(DISTINCT t.customer_id)          AS active_customers,
           COUNT(DISTINCT t.customer_id) FILTER (
               WHERE date_trunc('month', f.first_ts) = date_trunc('month', t.invoice_ts)
           ) AS new_customers
    FROM v_paid_order_totals t
    JOIN first_paid f USING (customer_id)
    GROUP BY 1
)
SELECT month,
       orders,
       active_customers,
       new_customers,
       active_customers - new_customers AS returning_customers,
       ROUND(new_customers::numeric / NULLIF(active_customers, 0) * 100, 1) AS new_share_pct
FROM monthly
ORDER BY month;
