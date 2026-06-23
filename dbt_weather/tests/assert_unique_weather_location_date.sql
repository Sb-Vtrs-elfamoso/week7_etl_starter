select
    location_id,
    weather_date,
    count(*) as row_count
from {{ ref('stg_weather_daily') }}
group by location_id, weather_date
having count(*) > 1