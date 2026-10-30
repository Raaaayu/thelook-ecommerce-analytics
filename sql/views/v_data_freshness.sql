-- "Data as of" tile: when the dashboard read the data and the newest record in each source table.
-- Events have future-dated records (A1), so they are capped at the current time.
SELECT
  CURRENT_TIMESTAMP()                                                             AS checked_at,
  (SELECT MAX(created_at) FROM `bigquery-public-data.thelook_ecommerce.orders`)   AS orders_max_created_at,
  (SELECT MAX(created_at) FROM `bigquery-public-data.thelook_ecommerce.users`)    AS users_max_created_at,
  (SELECT MAX(created_at) FROM `bigquery-public-data.thelook_ecommerce.events`
   WHERE created_at <= CURRENT_TIMESTAMP())                                       AS events_max_created_at,
  (SELECT COUNT(*) FROM `bigquery-public-data.thelook_ecommerce.orders`)          AS orders_total
