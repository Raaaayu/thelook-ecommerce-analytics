-- Kafelek „Dane na”: moment odczytu i najnowszy rekord w każdej tabeli źródłowej.
-- Events mają rekordy z datą w przyszłości (A1), więc ograniczamy je do bieżącej chwili.
SELECT
  CURRENT_TIMESTAMP()                                                             AS checked_at,
  (SELECT MAX(created_at) FROM `bigquery-public-data.thelook_ecommerce.orders`)   AS orders_max_created_at,
  (SELECT MAX(created_at) FROM `bigquery-public-data.thelook_ecommerce.users`)    AS users_max_created_at,
  (SELECT MAX(created_at) FROM `bigquery-public-data.thelook_ecommerce.events`
   WHERE created_at <= CURRENT_TIMESTAMP())                                       AS events_max_created_at,
  (SELECT COUNT(*) FROM `bigquery-public-data.thelook_ecommerce.orders`)          AS orders_total
