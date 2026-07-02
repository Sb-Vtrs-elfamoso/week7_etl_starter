/*
Lab 7.4B answer - SQL-based SCD Type 2 loading with manual surrogate-key generation.

This version uses load-date based SCD2:
- Next load date = last_successful_load_date + 1 day
- The log is intentionally initialized to 2026-06-23 in setup script 01
- Therefore, the first procedure run uses 2026-06-24
- The second procedure run uses 2026-06-25

Tracked SCD2 attributes:
first_name, last_name, email, phone, city, country_code, marketing_consent

Not tracked:
customer_sk, customer_business_key, completeness_score, row_hash,
valid_from, valid_to, is_current, load_run_id, loaded_at
*/

DROP PROCEDURE IF EXISTS usp_load_dim_customer_scd2;
GO
DROP TABLE IF EXISTS dim_customer_scd2;
GO

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

CREATE UNIQUE INDEX UX_dim_customer_scd2_current
ON dim_customer_scd2(customer_business_key)
WHERE is_current = 1;
GO

CREATE OR ALTER PROCEDURE usp_load_dim_customer_scd2
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @ProcessName varchar(100) = 'dim_customer_scd2';
    DECLARE @LoadRunId uniqueidentifier = NEWID();
    DECLARE @LoadedAt datetime2(0) = SYSUTCDATETIME();
    DECLARE @LoadDate date;
    DECLARE @MaxCustomerSk bigint;
    DECLARE @RowsToInsert int;
    DECLARE @ClosedRows int;

    SELECT
        @LoadDate = DATEADD(day, 1, last_successful_load_date)
    FROM etl_load_log
    WHERE process_name = @ProcessName;

    IF @LoadDate IS NULL
    BEGIN
        THROW 50000, 'No load log row found for dim_customer_scd2, or last_successful_load_date is NULL.', 1;
    END;

    BEGIN TRANSACTION;

    DROP TABLE IF EXISTS #stage;
    DROP TABLE IF EXISTS #rows_to_insert;

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
    INTO #stage
    FROM customer_golden_stage;

    IF EXISTS (
        SELECT customer_business_key
        FROM #stage
        GROUP BY customer_business_key
        HAVING COUNT(*) > 1
    )
    BEGIN
        THROW 50001, 'customer_golden_stage contains duplicate customer_business_key values.', 1;
    END;

    SELECT src.*
    INTO #rows_to_insert
    FROM #stage AS src
    LEFT JOIN dim_customer_scd2 AS tgt
        ON tgt.customer_business_key = src.customer_business_key
       AND tgt.is_current = 1
    WHERE tgt.customer_business_key IS NULL
       OR tgt.row_hash <> src.row_hash;

    SELECT @RowsToInsert = COUNT(*)
    FROM #rows_to_insert;

    UPDATE tgt
    SET
        valid_to = @LoadDate,
        is_current = 0
    FROM dim_customer_scd2 AS tgt
    JOIN #stage AS src
        ON src.customer_business_key = tgt.customer_business_key
    WHERE tgt.is_current = 1
      AND tgt.row_hash <> src.row_hash;

    SET @ClosedRows = @@ROWCOUNT;

    SELECT @MaxCustomerSk = COALESCE(MAX(customer_sk), 0)
    FROM dim_customer_scd2 WITH (UPDLOCK, HOLDLOCK);

    WITH numbered_rows AS
    (
        SELECT
            src.*,
            ROW_NUMBER() OVER (ORDER BY src.customer_business_key) AS rn
        FROM #rows_to_insert AS src
    )
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
        @MaxCustomerSk + rn AS customer_sk,
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
        CAST(1 AS bit) AS is_current,
        @LoadRunId AS load_run_id,
        @LoadedAt AS loaded_at
    FROM numbered_rows;

    UPDATE etl_load_log
    SET
        last_successful_load_date = @LoadDate,
        last_successful_load_at = @LoadedAt,
        last_load_run_id = @LoadRunId
    WHERE process_name = @ProcessName;

    COMMIT TRANSACTION;

    SELECT
        @LoadRunId AS load_run_id,
        @LoadDate AS load_date,
        @LoadedAt AS loaded_at,
        @ClosedRows AS closed_rows,
        @RowsToInsert AS inserted_rows;
END;
GO
