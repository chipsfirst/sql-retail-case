-- Вопрос: на какие сегменты делятся клиенты по давности, частоте и деньгам?
-- R: 1 — покупал давно, 5 — недавно. F и M: 5 — максимум.
WITH bounds AS (
    SELECT MAX(invoice_ts)::date AS max_date FROM v_paid_order_totals
),
rfm AS (
    SELECT t.customer_id,
           (SELECT max_date FROM bounds) - MAX(t.invoice_ts)::date AS recency_days,
           COUNT(*)                                               AS frequency,
           SUM(t.revenue)                                         AS monetary
    FROM v_paid_order_totals t
    WHERE t.customer_id IS NOT NULL
    GROUP BY t.customer_id
),
scored AS (
    SELECT r.*,
           NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
           NTILE(5) OVER (ORDER BY frequency)         AS f_score,
           NTILE(5) OVER (ORDER BY monetary)          AS m_score
    FROM rfm r
),
labeled AS (
    SELECT *,
           CASE
               WHEN r_score >= 4 AND f_score >= 4 THEN 'ядро'
               WHEN r_score >= 4 AND f_score <= 2 THEN 'новички'
               WHEN r_score <= 2 AND f_score >= 4 THEN 'спящие лояльные'
               WHEN r_score <= 2 AND f_score <= 2 THEN 'потерянные'
               ELSE 'середина'
           END AS segment
    FROM scored
)
SELECT segment,
       COUNT(*)                          AS customers,
       ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) AS customers_share_pct,
       ROUND(AVG(recency_days), 0)       AS avg_recency_days,
       ROUND(AVG(frequency), 2)          AS avg_orders,
       ROUND(AVG(monetary), 2)           AS avg_lifetime_revenue
FROM labeled
GROUP BY segment
ORDER BY customers DESC;
