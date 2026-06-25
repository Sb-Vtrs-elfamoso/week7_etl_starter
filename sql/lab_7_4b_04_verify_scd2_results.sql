/* Lab 7.4B - verification queries */

-- Current rows. Expected after second load: 11 rows.
SELECT
    customer_sk,
    customer_business_key,
    first_name,
    last_name,
    phone,
    city,
    country_code,
    marketing_consent,
    valid_from,
    valid_to,
    is_current
FROM dim_customer_scd2
WHERE is_current = 1
ORDER BY customer_business_key;
GO

-- Full row count. Expected after second load: 14 rows.
SELECT COUNT(*) AS total_scd2_rows
FROM dim_customer_scd2;
GO

-- Closed rows. Expected after second load: 3 rows.
SELECT COUNT(*) AS closed_rows
FROM dim_customer_scd2
WHERE is_current = 0;
GO

-- There must be no duplicate current rows per business key. Expected: 0 rows.
SELECT customer_business_key, COUNT(*) AS current_count
FROM dim_customer_scd2
WHERE is_current = 1
GROUP BY customer_business_key
HAVING COUNT(*) > 1;
GO

-- Inspect history for changed customers.
SELECT
    customer_sk,
    customer_business_key,
    phone,
    city,
    marketing_consent,
    valid_from,
    valid_to,
    is_current
FROM dim_customer_scd2
WHERE customer_business_key IN
(
    'anna.virtanen@example.com',
    'john.smith@example.com',
    'liisa.laine@example.com'
)
ORDER BY customer_business_key, valid_from, customer_sk;
GO

-- Load log should show 2026-06-25 after the second run.
SELECT * FROM etl_load_log;
GO
