-- Вопрос: в каких странах клиенты чаще возвращаются за второй покупкой?
WITH top_countries AS (
    SELECT country
    FROM customers
    GROUP BY country
    ORDER BY COUNT(*) DESC
    LIMIT 8
),
per_customer AS (
    SELECT t.country,
           t.customer_id,
           COUNT(*) AS orders
    FROM v_paid_order_totals t
    WHERE t.customer_id IS NOT NULL
    GROUP BY 1, 2
)
SELECT p.country,
       COUNT(*)                                                AS customers,
       COUNT(*) FILTER (WHERE p.orders > 1)                    AS repeaters,
       ROUND(COUNT(*) FILTER (WHERE p.orders > 1)::numeric / COUNT(*) * 100, 1) AS repeat_rate_pct,
       ROUND(AVG(p.orders), 2)                                 AS orders_per_customer
FROM per_customer p
JOIN top_countries c USING (country)
GROUP BY p.country
ORDER BY customers DESC;
