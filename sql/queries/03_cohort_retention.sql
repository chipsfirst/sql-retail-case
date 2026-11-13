-- Вопрос: как удерживаются клиенты по когортам первого платежа?
WITH first_order AS (
    SELECT customer_id, date_trunc('month', MIN(invoice_ts))::date AS cohort
    FROM v_paid_order_totals
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
activity AS (
    SELECT f.cohort,
           f.customer_id,
           (EXTRACT(YEAR FROM t.invoice_ts) * 12 + EXTRACT(MONTH FROM t.invoice_ts))
           - (EXTRACT(YEAR FROM f.cohort) * 12 + EXTRACT(MONTH FROM f.cohort)) AS month_offset
    FROM first_order f
    JOIN v_paid_order_totals t USING (customer_id)
),
sizes AS (
    SELECT cohort, COUNT(*) AS customers FROM first_order GROUP BY 1
)
SELECT a.cohort,
       s.customers,
       COUNT(DISTINCT a.customer_id) FILTER (WHERE a.month_offset = 0) AS m0,
       COUNT(DISTINCT a.customer_id) FILTER (WHERE a.month_offset = 1) AS m1,
       COUNT(DISTINCT a.customer_id) FILTER (WHERE a.month_offset = 2) AS m2,
       COUNT(DISTINCT a.customer_id) FILTER (WHERE a.month_offset = 3) AS m3,
       ROUND(COUNT(DISTINCT a.customer_id) FILTER (WHERE a.month_offset = 1)::numeric
             / NULLIF(s.customers, 0) * 100, 1) AS retention_m1_pct,
       ROUND(COUNT(DISTINCT a.customer_id) FILTER (WHERE a.month_offset = 3)::numeric
             / NULLIF(s.customers, 0) * 100, 1) AS retention_m3_pct
FROM activity a
JOIN sizes s USING (cohort)
WHERE a.cohort BETWEEN DATE '2010-01-01' AND DATE '2011-09-01'
GROUP BY a.cohort, s.customers
ORDER BY a.cohort;
