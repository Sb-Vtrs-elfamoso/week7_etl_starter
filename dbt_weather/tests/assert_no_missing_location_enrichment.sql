select
    *
from {{ ref('mart_weather_daily_by_location') }}
where country_code is null