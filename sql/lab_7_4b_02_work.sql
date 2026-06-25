/*
Lab 7.4B - SQL SCD Type 2

Load golden customers into an SCD2 dimension using update + insert logic
*/

-- Warm-up 1 - Run initial stage setup
SELECT COUNT(*) AS stage_rows
FROM customer_golden_stage;

SELECT *
FROM etl_load_log;
GO

-- Warm-up 2 - Confirm the intentionally backdated load log
SELECT
    process_name,
    last_successful_load_date,
    DATEADD(day, 1, last_successful_load_date) AS next_load_date
FROM etl_load_log
WHERE process_name = 'dim_customer_scd2';

-- Expected:
-- last_successful_load_date = 2026-06-23
-- next_load_date = 2026-06-24
GO

-- Warm-up 3 - Create the SCD2 dimension table
DROP TABLE IF EXISTS dim_customer_scd2;

CREATE TABLE dim_customer_scd2
(
    customer_sk bigint NOT NULL,
    customer_business_key varchar(255) NOT NULL,
    first_name varchar(100) NULL,
    last_name varchar(100) NULL,
    email varchar(255) NULL,
    phone varchar(50) NULL,
    city varchar(100) NULL,
    country_code char(2) NULL,
    marketing_consent bit NULL,
    completeness_score int NULL,
    row_hash varbinary(32) NOT NULL,
    valid_from date NOT NULL,
    valid_to date NULL,
    is_current bit NOT NULL,
    load_run_id uniqueidentifier NOT NULL,
    loaded_at datetime2(0) NOT NULL,
    CONSTRAINT PK_dim_customer_scd2 PRIMARY KEY (customer_sk)
);
GO

-- Warm-up 4 - Create a reusable stage hash view
CREATE OR ALTER VIEW vw_stage_with_hash AS
SELECT
    customer_business_key,
    first_name,
    last_name,
    email,
    phone,
    city,
    country_code,
    marketing_consent,
    completeness_score,
    HASHBYTES(
        'SHA2_256',
        CONCAT_WS('|',
            COALESCE(first_name, ''),
            COALESCE(last_name, ''),
            COALESCE(email, ''),
            COALESCE(phone, ''),
            COALESCE(city, ''),
            COALESCE(country_code, ''),
            COALESCE(CONVERT(varchar(1), marketing_consent), '')
        )
    ) AS row_hash
FROM customer_golden_stage;
GO

SELECT
    customer_business_key,
    row_hash
FROM vw_stage_with_hash
ORDER BY customer_business_key;
GO

-- Warm-up 5 - Generate manual surrogate keys with ROW_NUMBER
DECLARE @MaxCustomerSk bigint = 0;

SELECT
    @MaxCustomerSk + ROW_NUMBER() OVER (ORDER BY customer_business_key) AS generated_customer_sk,
    customer_business_key
FROM customer_golden_stage
ORDER BY customer_business_key;
GO

-- Warm-up 6 - Find changed or new rows pattern
-- This pattern is used after the first load exists.
-- It returns rows that are new or different from the current SCD2 row.
CREATE OR ALTER VIEW vw_changed_or_new AS
SELECT src.*
FROM vw_stage_with_hash AS src
LEFT JOIN dim_customer_scd2 AS tgt
    ON tgt.customer_business_key = src.customer_business_key
    AND tgt.is_current = 1
WHERE tgt.customer_business_key IS NULL
    OR tgt.row_hash <> src.row_hash;
GO

SELECT customer_business_key
FROM vw_changed_or_new;
GO

-- Warm-up 7 - Close changed current rows pattern
-- Old current rows are closed with the new load date.
-- valid_to is an exclusive end date.
-- This version closes only rows where tracked attributes changed.
DECLARE @LoadDate date = '2026-06-25';

UPDATE tgt
SET
    valid_to = @LoadDate,
    is_current = 0
FROM dim_customer_scd2 AS tgt

JOIN vw_stage_with_hash AS src
    ON src.customer_business_key = tgt.customer_business_key

WHERE tgt.is_current = 1
    AND tgt.row_hash <> src.row_hash;
GO

-- Warm-up 8 - Check current row uniqueness
SELECT customer_business_key, COUNT(*) AS current_count
FROM dim_customer_scd2
WHERE is_current = 1
GROUP BY customer_business_key
HAVING COUNT(*) > 1;

-- Expected result after a correct load: 0 rows
GO

-- Warm-up 9 - Query a customer history
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
WHERE customer_business_key = 'anna.virtanen@example.com'
ORDER BY valid_from, customer_sk;
GO

-- Warm-up 10 - Reset the lab safely if needed
-- If you accidentally run the procedure too many times and the dates move forward,
-- reset the lab by running the setup script again:
-- sql/lab_7_4b_01_setup_initial_stage_and_log.sql

SELECT * FROM etl_load_log;
GO

-- Required base tasks
-- Task 3
DROP TABLE IF EXISTS dim_customer_scd2;

CREATE TABLE dim_customer_scd2
(
    customer_sk bigint NOT NULL,
    customer_business_key varchar(255) NOT NULL,
    first_name varchar(100) NULL,
    last_name varchar(100) NULL,
    email varchar(255) NULL,
    phone varchar(50) NULL,
    city varchar(100) NULL,
    country_code char(2) NULL,
    marketing_consent bit NULL,
    completeness_score int NULL,
    row_hash varbinary(32) NOT NULL,
    valid_from date NOT NULL,
    valid_to date NULL,
    is_current bit NOT NULL,
    load_run_id uniqueidentifier NOT NULL,
    loaded_at datetime2(0) NOT NULL,
    CONSTRAINT PK_dim_customer_scd2 PRIMARY KEY (customer_sk)
);
GO

-- Task 4
DECLARE @MaxCustomerSk bigint = 0;

SELECT
    @MaxCustomerSk + ROW_NUMBER() OVER (ORDER BY customer_business_key) AS generated_customer_sk,
    customer_business_key
FROM customer_golden_stage
ORDER BY customer_business_key;
GO

CREATE OR ALTER VIEW vw_stage_with_hash AS
SELECT
    customer_business_key,
    first_name,
    last_name,
    email,
    phone,
    city,
    country_code,
    marketing_consent,
    completeness_score,
    HASHBYTES(
        'SHA2_256',
        CONCAT_WS('|',
            COALESCE(first_name, ''),
            COALESCE(last_name, ''),
            COALESCE(email, ''),
            COALESCE(phone, ''),
            COALESCE(city, ''),
            COALESCE(country_code, ''),
            COALESCE(CONVERT(varchar(1), marketing_consent), '')
        )
    ) AS row_hash
FROM customer_golden_stage;
GO

CREATE OR ALTER VIEW vw_changed_or_new AS
SELECT src.*
FROM vw_stage_with_hash AS src
LEFT JOIN dim_customer_scd2 AS tgt
    ON tgt.customer_business_key = src.customer_business_key
    AND tgt.is_current = 1
WHERE tgt.customer_business_key IS NULL
    OR tgt.row_hash <> src.row_hash;
GO

-- Task 5
CREATE or ALTER PROCEDURE usp_load_dim_customer_scd2 AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @LoadRunId uniqueidentifier = NEWID();
    DECLARE @LoadedAt datetime2(0) = SYSDATETIME();
    DECLARE @LoadDate date;
    DECLARE @MaxCustomerSk bigint;
    DECLARE @ClosedRows int;
    DECLARE @InsertedRows int;

    SELECT
        @MaxCustomerSk = ISNULL(MAX(customer_sk), 0)
    FROM dim_customer_scd2;

    SELECT
        @LoadDate = DATEADD(day, 1, last_successful_load_date)
    FROM etl_load_log
    WHERE process_name = 'dim_customer_scd2';

    UPDATE tgt
    SET
        valid_to = @LoadDate,
        is_current = 0
    FROM dim_customer_scd2 AS tgt
    JOIN vw_changed_or_new AS src
        ON src.customer_business_key = tgt.customer_business_key
    WHERE tgt.is_current = 1;

    SET @ClosedRows = @@ROWCOUNT;

    INSERT INTO dim_customer_scd2
    (
        customer_sk,
        customer_business_key,
        first_name,
        last_name,
        email,
        phone,
        city,
        country_code,
        marketing_consent,
        completeness_score,
        row_hash,
        valid_from,
        valid_to,
        is_current,
        load_run_id,
        loaded_at
    )
    SELECT
        @MaxCustomerSk + ROW_NUMBER() OVER (ORDER BY customer_business_key) AS customer_sk,
        customer_business_key,
        first_name,
        last_name,
        email,
        phone,
        city,
        country_code,
        marketing_consent,
        completeness_score,
        row_hash,
        @LoadDate AS valid_from,
        NULL AS valid_to,
        1 AS is_current,
        @LoadRunId AS load_run_id,
        @LoadedAt AS loaded_at
    FROM vw_changed_or_new;

    SET @InsertedRows = @@ROWCOUNT;

    UPDATE etl_load_log
    SET
        last_successful_load_date = @LoadDate,
        last_successful_load_at = @LoadedAt,
        last_load_run_id = @LoadRunId
    WHERE process_name = 'dim_customer_scd2';

    SELECT
        @LoadDate AS load_date,
        @ClosedRows AS closed_rows,
        @InsertedRows AS inserted_rows;
END;
GO

-- Task 6 - 9
EXEC usp_load_dim_customer_scd2;
GO

-- Task 7
SELECT * FROM dim_customer_scd2;
GO

-- Practice Tasks
-- Task 1
SELECT * FROM dim_customer_scd2
WHERE customer_business_key = 'anna.virtanen@example.com';
GO

-- Task 2
SELECT * FROM dim_customer_scd2
WHERE customer_business_key = 'john.smith@example.com';
GO

-- Task 3
SELECT * FROM dim_customer_scd2
WHERE customer_business_key = 'liisa.laine@example.com';
GO

-- Task 4
SELECT * FROM dim_customer_scd2
WHERE customer_business_key not IN (
    SELECT customer_business_key FROM dim_customer_scd2
    WHERE valid_from < (SELECT MAX(valid_from) FROM dim_customer_scd2)
);
GO

-- Task 5
SELECT * FROM etl_load_log;
GO