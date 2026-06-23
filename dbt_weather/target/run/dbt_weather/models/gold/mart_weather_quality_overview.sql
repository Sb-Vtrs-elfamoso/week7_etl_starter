
  
    USE [de_etl_db];
    USE [de_etl_db];
    
    

    

    
    USE [de_etl_db];
    EXEC('
        CREATE OR ALTER VIEW "student10"."mart_weather_quality_overview__dbt_tmp__dbt_tmp_vw" AS 

select
    ''accepted_weather_rows'' as metric_name,
    count(*) as metric_value
from "de_etl_db"."student10"."stg_weather_daily"

union all

select
    ''rejected_weather_rows'' as metric_name,
    count(*) as metric_value
from "de_etl_db"."student10"."rejected_weather_rows"

union all

select
    ''gold_weather_rows'' as metric_name,
    count(*) as metric_value
from "de_etl_db"."student10"."mart_weather_daily_by_location";
    ')

EXEC('
            SELECT * INTO "de_etl_db"."student10"."mart_weather_quality_overview__dbt_tmp" FROM "de_etl_db"."student10"."mart_weather_quality_overview__dbt_tmp__dbt_tmp_vw" 
    OPTION (LABEL = ''dbt-sqlserver'');

        ')

    
    EXEC('DROP VIEW IF EXISTS "student10"."mart_weather_quality_overview__dbt_tmp__dbt_tmp_vw"')



    
    use [de_etl_db];
    if EXISTS (
        SELECT *
        FROM sys.indexes with (nolock)
        WHERE name = 'student10_mart_weather_quality_overview__dbt_tmp_cci'
        AND object_id=object_id('student10_mart_weather_quality_overview__dbt_tmp')
    )
    DROP index "student10"."mart_weather_quality_overview__dbt_tmp".student10_mart_weather_quality_overview__dbt_tmp_cci
    CREATE CLUSTERED COLUMNSTORE INDEX student10_mart_weather_quality_overview__dbt_tmp_cci
    ON "student10"."mart_weather_quality_overview__dbt_tmp"

   


  