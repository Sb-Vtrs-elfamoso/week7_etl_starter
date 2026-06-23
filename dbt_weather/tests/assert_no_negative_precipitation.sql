select
    location_id,
    weather_date,
    total_precip_mm
from {{ ref('stg_weather_daily') }}
where total_precip_mm < 0