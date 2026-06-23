select
    location_id,
    weather_date,
    count(*) as row_count
from "de_etl_db"."student10"."stg_weather_daily"
group by location_id, weather_date
having count(*) > 1