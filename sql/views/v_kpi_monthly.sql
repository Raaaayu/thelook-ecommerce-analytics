-- KPI miesięczne (jeden wiersz na miesiąc).
-- Tylko pełne miesiące; data z orders.created_at (order_items.created_at jest niewiarygodne, zob. A1);
-- przychód = Complete + Shipped; powracający = 2. i kolejne zamówienie klienta (numeracja po WSZYSTKICH zamówieniach).
WITH order_value AS (
  SELECT order_id, SUM(sale_price) AS order_value
  FROM `bigquery-public-data.thelook_ecommerce.order_items`
  GROUP BY order_id
),
orders AS (
  SELECT
    o.order_id,
    o.user_id,
    o.status,
    o.created_at,
    COALESCE(v.order_value, 0) AS order_value,
    o.status IN ('Complete', 'Shipped') AS is_revenue,
    ROW_NUMBER() OVER (PARTITION BY o.user_id ORDER BY o.created_at) AS order_rank
  FROM `bigquery-public-data.thelook_ecommerce.orders` AS o
  LEFT JOIN order_value AS v USING (order_id)
)
SELECT
  DATE_TRUNC(DATE(created_at), MONTH)                                  AS month,
  COUNT(*)                                                             AS orders,
  COUNTIF(is_revenue)                                                  AS revenue_orders,
  COUNT(DISTINCT user_id)                                              AS active_customers,
  SUM(IF(is_revenue, order_value, 0))                                  AS revenue,
  SUM(IF(is_revenue AND order_rank = 1, order_value, 0))               AS revenue_new,
  SUM(IF(is_revenue AND order_rank > 1, order_value, 0))               AS revenue_returning,
  SAFE_DIVIDE(SUM(IF(is_revenue, order_value, 0)), COUNTIF(is_revenue)) AS aov,
  COUNTIF(status = 'Cancelled')                                        AS cancelled_orders,  -- liczniki, żeby dashboard
  COUNTIF(status = 'Returned')                                         AS returned_orders,   -- liczył wskaźniki dla dowolnego okresu
  SAFE_DIVIDE(COUNTIF(status = 'Cancelled'), COUNT(*))                 AS cancel_rate,
  SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNT(*))                  AS return_rate,
  SUM(IF(status IN ('Cancelled', 'Returned'), order_value, 0))         AS lost_value
FROM orders
WHERE created_at < TIMESTAMP(DATE_TRUNC(CURRENT_DATE(), MONTH))
GROUP BY month
