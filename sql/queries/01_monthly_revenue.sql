-- Вопрос: как менялась выручка по месяцам и каков темп роста месяц к месяцу?
-- Только оплаченные заказы; декабрь 2011 обрезан (данные до 9 декабря).
WITH monthly AS (
    SELECT date_trunc('month', invoice_ts)::date AS month,
           COUNT(*)                             AS orders,
           SUM(revenue)                         AS revenue
    FROM v_paid_order_totals
    GROUP BY 1
)
SELECT month,
       orders,
       revenue,
       ROUND(revenue / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100 - 100, 1) AS mom_pct,
       ROUND(revenue / orders, 2)                                                    AS aov
FROM monthly
ORDER BY month;
