-- Вопрос: как менялась выручка по месяцам и каков темп роста месяц к месяцу?
-- Учитываются только оплаченные заказы (v_paid_order_totals).
WITH monthly AS (
    SELECT date_trunc('month', order_ts)::date AS month,
           COUNT(*)                          AS orders,
           SUM(revenue)                      AS revenue
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
