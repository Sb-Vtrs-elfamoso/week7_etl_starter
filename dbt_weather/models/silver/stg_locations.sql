{{ config(materialized='view', tags=['weather', 'silver']) }}

select
    location_id,
    city,
    country_code,
    country_name,
    latitude,
    longitude,
    region,
    climate_zone
from {{ source('shared', 'src_locations') }}