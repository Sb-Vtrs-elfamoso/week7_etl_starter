

select
    MONTH(w.weather_date) as month,
    YEAR(w.weather_date) as year,
    w.location_id,
    l.city,
    AVG(w.avg_temp_c) as avg_temp_c,
    MAX(w.max_temp_c) as max_temp_c,
    MIN(w.min_temp_c) as min_temp_c,
    SUM(w.total_precip_mm) as total_precip_mm,
    AVG(w.avg_humidity_pct) as avg_humidity_pct,
    AVG(w.avg_wind_speed_kmh) as avg_wind_speed_kmh
    
from "de_etl_db"."student10"."stg_weather_daily" as w
left join "de_etl_db"."student10"."stg_locations" as l
    on w.location_id = l.location_id

group by 
    MONTH(w.weather_date),
    YEAR(w.weather_date),
    w.location_id,
    l.city