select
    location_id,
    weather_date,
    total_precip_mm
from "de_etl_db"."student10"."stg_weather_daily"
where total_precip_mm < 0