/*
Lab 7.4B - setup initial customer_golden_stage and load log.
Run this in Azure SQL while connected as your own student user.
Objects are created in your default schema, for example student01.

Important training setup:
The load log is intentionally initialized to 2026-06-23.
The procedure uses DATEADD(day, 1, last_successful_load_date) as the next load date,
so the first lab load will get load date 2026-06-24.
*/

DROP TABLE IF EXISTS dim_customer_scd2;
GO
DROP TABLE IF EXISTS customer_golden_stage;
GO
DROP TABLE IF EXISTS etl_load_log;
GO

CREATE TABLE customer_golden_stage
(
    customer_business_key varchar(255) NOT NULL,
    first_name varchar(100) NULL,
    last_name varchar(100) NULL,
    email varchar(255) NULL,
    phone varchar(50) NULL,
    city varchar(100) NULL,
    country_code char(2) NULL,
    marketing_consent bit NULL,
    completeness_score int NULL
);
GO

CREATE TABLE etl_load_log
(
    process_name varchar(100) NOT NULL PRIMARY KEY,
    last_successful_load_date date NULL,
    last_successful_load_at datetime2(0) NULL,
    last_load_run_id uniqueidentifier NULL
);
GO

INSERT INTO etl_load_log
(
    process_name,
    last_successful_load_date,
    last_successful_load_at,
    last_load_run_id
)
VALUES
(
    'dim_customer_scd2',
    '2026-06-23',  -- intentionally one day before the first lab load date
    NULL,
    NULL
);
GO

INSERT INTO customer_golden_stage
(
    customer_business_key, first_name, last_name, email, phone, city,
    country_code, marketing_consent, completeness_score
)
VALUES
('anna.virtanen@example.com','Anna','Virtanen','anna.virtanen@example.com','+358401111111','Helsinki','FI',1,9),
('erik.svensson@example.com','Erik','Svensson','erik.svensson@example.com','+46701234567','Stockholm','SE',0,9),
('john.smith@example.com','John','Smith','john.smith@example.com','+447700900123','London','GB',1,9),
('laura.nieminen@example.com','Laura','Nieminen','laura.nieminen@example.com','+358403333333','Turku','FI',1,8),
('liisa.laine@example.com','Liisa','Laine','liisa.laine@example.com','+358405555555','Helsinki','FI',1,9),
('maria.garcia@example.com','Maria','Garcia','maria.garcia@example.com','+34911222333','Madrid','ES',1,8),
('matti.korhonen@example.com','Matti','Korhonen','matti.korhonen@example.com','+358402222222','Tampere','FI',0,9),
('nina.berg@example.com','Nina','Berg','nina.berg@example.com','+4798765432','Oslo','NO',1,9),
('peter.hansen@example.com','Peter','Hansen','peter.hansen@example.com','+4522334455','Copenhagen','DK',1,9),
('sofia.rossi@example.com','Sofia','Rossi','sofia.rossi@example.com','+3906123456','Milan','IT',1,9);
GO

SELECT * FROM etl_load_log;
SELECT * FROM customer_golden_stage ORDER BY customer_business_key;
GO