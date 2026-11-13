-- Вопрос: как заказы и выручка распределены по дням недели?
SELECT TRIM(TO_CHAR(invoice_ts, 'Day')) AS weekday,
       EXTRACT(ISODOW FROM invoice_ts)   AS dow,
       COUNT(*)                          AS orders,
       SUM(revenue)                      AS revenue,
       ROUND(AVG(revenue), 2)            AS avg_check
FROM v_paid_order_totals
GROUP BY 1, 2
ORDER BY 2;
