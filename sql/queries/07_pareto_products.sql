-- Вопрос: какая доля товаров даёт основную выручку (правило Парето)?
WITH by_product AS (
    SELECT p.product_id,
           p.name,
           p.category,
           SUM(i.quantity * i.unit_price * (1 - i.discount)) AS revenue
    FROM order_items i
    JOIN orders o   USING (order_id)
    JOIN products p USING (product_id)
    WHERE o.status = 'paid'
    GROUP BY 1, 2, 3
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (ORDER BY revenue DESC, product_id) AS rn,
           SUM(revenue) OVER (ORDER BY revenue DESC, product_id) AS cumulative_revenue,
           SUM(revenue) OVER ()                                  AS total_revenue,
           COUNT(*) OVER ()                                      AS total_products
    FROM by_product
)
SELECT rn,
       name,
       category,
       revenue,
       ROUND(cumulative_revenue / total_revenue * 100, 1) AS cumulative_share_pct
FROM ranked
WHERE rn <= 10
ORDER BY rn;
