-- Вопрос: какая доля товаров даёт основную выручку (правило Парето)?
WITH by_product AS (
    SELECT p.stock_code,
           p.description,
           SUM(i.quantity * i.unit_price) AS revenue
    FROM order_items i
    JOIN orders o   USING (invoice_no)
    JOIN products p USING (stock_code)
    WHERE o.status = 'paid'
    GROUP BY 1, 2
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (ORDER BY revenue DESC, stock_code) AS rn,
           SUM(revenue) OVER (ORDER BY revenue DESC, stock_code) AS cumulative_revenue,
           SUM(revenue) OVER ()                                  AS total_revenue,
           COUNT(*) OVER ()                                      AS total_products
    FROM by_product
)
SELECT rn,
       description,
       revenue,
       ROUND(cumulative_revenue / total_revenue * 100, 2) AS cumulative_share_pct
FROM ranked
WHERE rn <= 10
ORDER BY rn;
