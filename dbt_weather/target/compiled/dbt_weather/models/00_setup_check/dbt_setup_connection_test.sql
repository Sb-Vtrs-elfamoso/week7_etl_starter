/*
    Setup check model.

    This model exists only to verify that:
    - dbt is installed
    - profiles.yml works
    - Azure SQL connection works
    - dbt can create a view in your own schema

    It is not part of the actual weather ETL lab.
*/

select
    cast(1 as int) as id,
    cast('dbt setup check' as varchar(100)) as description_text