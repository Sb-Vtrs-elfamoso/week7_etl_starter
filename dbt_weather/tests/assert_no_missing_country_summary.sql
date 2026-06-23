select
    *
from {{ ref('mart_weather_daily_by_country_summary') }}
where country_code is null