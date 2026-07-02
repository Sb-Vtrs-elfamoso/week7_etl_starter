-- This is basic version without any checks, temporary tables or CTE's

CREATE OR ALTER PROCEDURE usp_load_dim_customer_scd2
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ProcessName varchar(100) = 'dim_customer_scd2';
    DECLARE @LoadRunId uniqueidentifier = NEWID();
    DECLARE @LoadedAt datetime2(0) = SYSUTCDATETIME();
    DECLARE @LoadDate date;
    DECLARE @MaxCustomerSk bigint;
    DECLARE @ClosedRows int;
    DECLARE @InsertedRows int;

    -- Get the next simulated load date from the load log and add one day to that
    -- not using the getdate() here bacuse the dates are simulated

    SELECT
        @LoadDate = DATEADD(day, 1, last_successful_load_date)
    FROM etl_load_log
    WHERE process_name = @ProcessName;

    -- Step 1:
    -- Close current rows where tracked customer attributes have changed.
    -- This is the SCD Type 2 "close old version" step.
    UPDATE tgt
    SET
        valid_to = @LoadDate,
        is_current = 0
    FROM dim_customer_scd2 AS tgt
    JOIN customer_golden_stage AS src
        ON src.customer_business_key = tgt.customer_business_key
    WHERE tgt.is_current = 1
      AND tgt.row_hash <> HASHBYTES(
            'SHA2_256',
            CONCAT_WS('|',
                COALESCE(src.first_name, ''),
                COALESCE(src.last_name, ''),
                COALESCE(src.email, ''),
                COALESCE(src.phone, ''),
                COALESCE(src.city, ''),
                COALESCE(src.country_code, ''),
                COALESCE(CONVERT(varchar(1), src.marketing_consent), '')
            )
        );

    SET @ClosedRows = @@ROWCOUNT;

    -- Step 2:
    -- Read the current highest surrogate key.
    SELECT
        @MaxCustomerSk = COALESCE(MAX(customer_sk), 0)
    FROM dim_customer_scd2;

    -- Step 3:
    -- Insert rows that do not currently have an active version.
    --
    -- This includes:
    --   - brand new customers
    --   - changed customers, because their old current row was closed above
    --
    -- It does not include unchanged customers, because they still have a current row.
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
        @MaxCustomerSk + ROW_NUMBER() OVER (ORDER BY src.customer_business_key) AS customer_sk,
        src.customer_business_key,
        src.first_name,
        src.last_name,
        src.email,
        src.phone,
        src.city,
        src.country_code,
        src.marketing_consent,
        src.completeness_score,
        HASHBYTES(
            'SHA2_256',
            CONCAT_WS('|',
                COALESCE(src.first_name, ''),
                COALESCE(src.last_name, ''),
                COALESCE(src.email, ''),
                COALESCE(src.phone, ''),
                COALESCE(src.city, ''),
                COALESCE(src.country_code, ''),
                COALESCE(CONVERT(varchar(1), src.marketing_consent), '')
            )
        ) AS row_hash,
        @LoadDate AS valid_from,
        NULL AS valid_to,
        CAST(1 AS bit) AS is_current,
        @LoadRunId AS load_run_id,
        @LoadedAt AS loaded_at
    FROM customer_golden_stage AS src
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM dim_customer_scd2 AS tgt
        WHERE tgt.customer_business_key = src.customer_business_key
          AND tgt.is_current = 1
    );

    SET @InsertedRows = @@ROWCOUNT; -- This system variable @@rowcount contains the last executed sql-statement row count 

    -- Step 4:
    -- Advance the load log after the close and insert steps.
    UPDATE etl_load_log
    SET
        last_successful_load_date = @LoadDate,
        last_successful_load_at = @LoadedAt,
        last_load_run_id = @LoadRunId
    WHERE process_name = @ProcessName;

    -- Step 5:
    -- Return a simple result summary.
    SELECT
        @LoadRunId AS load_run_id,
        @LoadDate AS load_date,
        @LoadedAt AS loaded_at,
        @ClosedRows AS closed_rows,
        @InsertedRows AS inserted_rows;
END;
GO