-- Wartość klienta wg segmentu (A2): wiersz = płeć x grupa wieku x kraj x kanał pozyskania.
-- Użytkownicy bez zakupów zostają (LEFT JOIN + COALESCE); przychód = Complete + Shipped.
WITH user_revenue AS (
  SELECT
    o.user_id,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.sale_price)         AS revenue
  FROM `bigquery-public-data.thelook_ecommerce.orders` AS o
  JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi USING (order_id)
  WHERE o.status IN ('Complete', 'Shipped')
  GROUP BY o.user_id
)
SELECT
  u.gender,
  CASE
    WHEN u.age < 18 THEN '12-17'
    WHEN u.age < 25 THEN '18-24'
    WHEN u.age < 35 THEN '25-34'
    WHEN u.age < 45 THEN '35-44'
    WHEN u.age < 55 THEN '45-54'
    WHEN u.age < 65 THEN '55-64'
    ELSE '65+'
  END                                 AS age_group,
  u.country,
  u.traffic_source                    AS acquisition_source,
  COUNT(*)                            AS users,
  COUNTIF(r.orders > 0)               AS buyers,
  COALESCE(SUM(r.orders), 0)          AS orders,
  COALESCE(SUM(r.revenue), 0)         AS revenue
FROM `bigquery-public-data.thelook_ecommerce.users` AS u
LEFT JOIN user_revenue AS r ON r.user_id = u.id
GROUP BY gender, age_group, country, acquisition_source
