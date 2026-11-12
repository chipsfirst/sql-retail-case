-- Вопрос: насколько средний чек расходится с медианой и есть ли выбросы?
SELECT date_trunc('month', order_ts)::date AS month,
       COUNT(*)                            AS orders,
       ROUND(AVG(revenue), 2)              AS avg_check,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY revenue)::numeric, 2) AS median_check,
       ROUND(MAX(revenue), 2)              AS max_check
FROM v_paid_order_totals
GROUP BY 1
ORDER BY 1;
