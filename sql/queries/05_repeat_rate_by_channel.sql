-- Вопрос: клиенты из какого канала чаще возвращаются за второй покупкой?
WITH per_customer AS (
    SELECT c.channel,
           t.customer_id,
           COUNT(*) AS orders
    FROM v_paid_order_totals t
    JOIN customers c USING (customer_id)
    GROUP BY 1, 2
)
SELECT channel,
       COUNT(*)                                                AS customers,
       COUNT(*) FILTER (WHERE orders > 1)                      AS repeaters,
       ROUND(COUNT(*) FILTER (WHERE orders > 1)::numeric / COUNT(*) * 100, 1) AS repeat_rate_pct,
       ROUND(AVG(orders), 2)                                   AS orders_per_customer
FROM per_customer
GROUP BY channel
ORDER BY repeat_rate_pct DESC;
