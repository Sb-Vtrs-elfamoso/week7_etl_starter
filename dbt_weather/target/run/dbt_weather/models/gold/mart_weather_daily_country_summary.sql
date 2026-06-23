
  
    USE [de_etl_db];
    USE [de_etl_db];
    
    

    

    
    USE [de_etl_db];
    EXEC('
        CREATE OR ALTER VIEW "student10"."mart_weather_daily_country_summary__dbt_tmp__dbt_tmp_vw" AS 

select
    w.weather_date,
    l.country_code,
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
    w.weather_date,
    l.country_code;
    ')

EXEC('
            SELECT * INTO "de_etl_db"."student10"."mart_weather_daily_country_summary__dbt_tmp" FROM "de_etl_db"."student10"."mart_weather_daily_country_summary__dbt_tmp__dbt_tmp_vw" 
    OPTION (LABEL = ''dbt-sqlserver'');

        ')

    
    EXEC('DROP VIEW IF EXISTS "student10"."mart_weather_daily_country_summary__dbt_tmp__dbt_tmp_vw"')



    
    use [de_etl_db];
    if EXISTS (
        SELECT *
        FROM sys.indexes with (nolock)
        WHERE name = 'student10_mart_weather_daily_country_summary__dbt_tmp_cci'
        AND object_id=object_id('student10_mart_weather_daily_country_summary__dbt_tmp')
    )
    DROP index "student10"."mart_weather_daily_country_summary__dbt_tmp".student10_mart_weather_daily_country_summary__dbt_tmp_cci
    CREATE CLUSTERED COLUMNSTORE INDEX student10_mart_weather_daily_country_summary__dbt_tmp_cci
    ON "student10"."mart_weather_daily_country_summary__dbt_tmp"

   


  