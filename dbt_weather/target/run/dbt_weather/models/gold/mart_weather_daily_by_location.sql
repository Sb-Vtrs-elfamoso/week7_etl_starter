
  
    USE [de_etl_db];
    USE [de_etl_db];
    
    

    

    
    USE [de_etl_db];
    EXEC('
        CREATE OR ALTER VIEW "student10"."mart_weather_daily_by_location__dbt_tmp__dbt_tmp_vw" AS 

select
    w.weather_date,
    w.location_id,
    l.city,
    l.country_code,
    l.country_name,
    l.region,
    l.climate_zone,
    w.avg_temp_c,
    w.max_temp_c,
    w.min_temp_c,
    w.total_precip_mm,
    w.avg_humidity_pct,
    w.avg_wind_speed_kmh
    
from "de_etl_db"."student10"."stg_weather_daily" as w
left join "de_etl_db"."student10"."stg_locations" as l
    on w.location_id = l.location_id;
    ')

EXEC('
            SELECT * INTO "de_etl_db"."student10"."mart_weather_daily_by_location__dbt_tmp" FROM "de_etl_db"."student10"."mart_weather_daily_by_location__dbt_tmp__dbt_tmp_vw" 
    OPTION (LABEL = ''dbt-sqlserver'');

        ')

    
    EXEC('DROP VIEW IF EXISTS "student10"."mart_weather_daily_by_location__dbt_tmp__dbt_tmp_vw"')



    
    use [de_etl_db];
    if EXISTS (
        SELECT *
        FROM sys.indexes with (nolock)
        WHERE name = 'student10_mart_weather_daily_by_location__dbt_tmp_cci'
        AND object_id=object_id('student10_mart_weather_daily_by_location__dbt_tmp')
    )
    DROP index "student10"."mart_weather_daily_by_location__dbt_tmp".student10_mart_weather_daily_by_location__dbt_tmp_cci
    CREATE CLUSTERED COLUMNSTORE INDEX student10_mart_weather_daily_by_location__dbt_tmp_cci
    ON "student10"."mart_weather_daily_by_location__dbt_tmp"

   


  