select
    location_id,
    avg_humidity_pct
from "de_etl_db"."student10"."stg_weather_daily"
where avg_humidity_pct < 0 or avg_humidity_pct > 100