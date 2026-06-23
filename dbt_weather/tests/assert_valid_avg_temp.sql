select
    location_id,
    avg_temp_c,
    min_temp_c,
    max_temp_c
from {{ ref('stg_weather_daily') }}
where avg_temp_c < min_temp_c or avg_temp_c > max_temp_c