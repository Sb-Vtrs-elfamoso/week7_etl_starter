

select
    location_id,
    city,
    cast(weather_date as date) as weather_date,
    avg_temp_c,
    max_temp_c,
    min_temp_c,
    total_precip_mm,
    avg_humidity_pct,
    avg_wind_speed_kmh,
    source_system,
    run_id,
    loaded_at,
    loaded_file_name
from "de_etl_db"."student10"."silver_weather_daily_clean"