-- Sprzedaż produktów wg miesiąca, działu i kategorii.
-- Status i data z orders (A1); zysk brutto = sale_price - koszt produktu (A3).
SELECT
  DATE_TRUNC(DATE(o.created_at), MONTH)                                         AS month,
  p.department,
  p.category,
  COUNT(*)                                                                      AS items,
  SUM(IF(o.status IN ('Complete', 'Shipped'), oi.sale_price, 0))                AS revenue,
  SUM(IF(o.status IN ('Complete', 'Shipped'), oi.sale_price - p.cost, 0))       AS gross_profit,
  SUM(IF(o.status IN ('Cancelled', 'Returned'), oi.sale_price, 0))              AS lost_value,
  COUNTIF(o.status = 'Cancelled')                                               AS cancelled_items,
  COUNTIF(o.status = 'Returned')                                                AS returned_items
FROM `bigquery-public-data.thelook_ecommerce.order_items` AS oi
JOIN `bigquery-public-data.thelook_ecommerce.orders` AS o USING (order_id)
JOIN `bigquery-public-data.thelook_ecommerce.products` AS p ON p.id = oi.product_id
WHERE o.created_at < TIMESTAMP(DATE_TRUNC(CURRENT_DATE(), MONTH))
GROUP BY month, department, category
