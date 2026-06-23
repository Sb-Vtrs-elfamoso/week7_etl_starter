{{ config(materialized='table', tags=['weather', 'gold', 'reporting']) }}

select
    w.weather_date,
    w.location_id,
    l.city,
    l.country_code,
    l.country_name,
    l.region,
    l.climate_zone,
    w.avg_temp_c,
    w.max_temp_c,
    w.min_temp_c,
    w.total_precip_mm,
    w.avg_humidity_pct,
    w.avg_wind_speed_kmh
    
from {{ ref('stg_weather_daily') }} as w
left join {{ ref('stg_locations') }} as l
    on w.location_id = l.location_id