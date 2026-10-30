-- Purchase funnel by month, session traffic source and login state (session level, A6).
WITH sessions AS (
  SELECT
    session_id,
    MIN(created_at)                     AS started_at,
    ANY_VALUE(traffic_source)           AS traffic_source,   -- one source per session (checked in A6)
    LOGICAL_OR(user_id IS NOT NULL)     AS logged_in,
    LOGICAL_OR(event_type = 'product')  AS saw_product,
    LOGICAL_OR(event_type = 'cart')     AS added_to_cart,
    LOGICAL_OR(event_type = 'cancel')   AS cancelled,
    LOGICAL_OR(event_type = 'purchase') AS purchased
  FROM `bigquery-public-data.thelook_ecommerce.events`
  WHERE created_at < TIMESTAMP(DATE_TRUNC(CURRENT_DATE(), MONTH))
  GROUP BY session_id
)
SELECT
  DATE_TRUNC(DATE(started_at), MONTH) AS month,
  traffic_source,
  logged_in,
  COUNT(*)               AS sessions,
  COUNTIF(saw_product)   AS product_sessions,
  COUNTIF(added_to_cart) AS cart_sessions,
  COUNTIF(cancelled)     AS cart_cancel_sessions,
  COUNTIF(purchased)     AS purchase_sessions
FROM sessions
GROUP BY month, traffic_source, logged_in
