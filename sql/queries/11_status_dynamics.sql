-- Вопрос: как менялась доля отмен и сколько денег возвращалось?
WITH monthly AS (
    SELECT date_trunc('month', invoice_ts)::date AS month,
           COUNT(*) FILTER (WHERE status = 'paid')      AS paid_invoices,
           COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled_invoices,
           SUM(revenue) FILTER (WHERE status = 'cancelled') AS cancelled_revenue
    FROM orders o
    JOIN (
        SELECT invoice_no, SUM(quantity * unit_price)::numeric(12, 2) AS revenue
        FROM order_items
        GROUP BY invoice_no
    ) i USING (invoice_no)
    GROUP BY 1
)
SELECT month,
       paid_invoices,
       cancelled_invoices,
       ROUND(cancelled_invoices::numeric / NULLIF(paid_invoices + cancelled_invoices, 0) * 100, 2)
             AS cancelled_share_pct,
       ROUND(cancelled_revenue, 2) AS cancelled_revenue
FROM monthly
ORDER BY month;
