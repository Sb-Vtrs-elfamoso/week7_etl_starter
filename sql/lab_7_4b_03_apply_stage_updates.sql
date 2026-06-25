/*
Lab 7.4B - replace stage with second current-state customer snapshot.
Run this after the first SCD2 load.

This script simulates the next nightly customer consolidation output.
The stage table always contains only the latest current-state view.
The SCD2 table stores the history.
*/

TRUNCATE TABLE customer_golden_stage;
GO

INSERT INTO customer_golden_stage
(
    customer_business_key, first_name, last_name, email, phone, city,
    country_code, marketing_consent, completeness_score
)
VALUES
('anna.virtanen@example.com','Anna','Virtanen','anna.virtanen@example.com','+358409999998','Espoo','FI',1,9),
('erik.svensson@example.com','Erik','Svensson','erik.svensson@example.com','+46701234567','Stockholm','SE',0,9),
('john.smith@example.com','John','Smith','john.smith@example.com','+447700900123','London','GB',0,9),
('laura.nieminen@example.com','Laura','Nieminen','laura.nieminen@example.com','+358403333333','Turku','FI',1,8),
('liisa.laine@example.com','Liisa','Laine','liisa.laine@example.com','+358405555555','Vantaa','FI',1,9),
('maria.garcia@example.com','Maria','Garcia','maria.garcia@example.com','+34911222333','Madrid','ES',1,8),
('matti.korhonen@example.com','Matti','Korhonen','matti.korhonen@example.com','+358402222222','Tampere','FI',0,9),
('nina.berg@example.com','Nina','Berg','nina.berg@example.com','+4798765432','Oslo','NO',1,9),
('peter.hansen@example.com','Peter','Hansen','peter.hansen@example.com','+4522334455','Copenhagen','DK',1,9),
('sofia.rossi@example.com','Sofia','Rossi','sofia.rossi@example.com','+3906123456','Milan','IT',1,9),
('emma.wilson@example.com','Emma','Wilson','emma.wilson@example.com','+447700111222','Manchester','GB',1,8);
GO

SELECT *
FROM customer_golden_stage
ORDER BY customer_business_key;
GO
