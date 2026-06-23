
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_c3c525084f4470d754e943686f3636a1_8486]
   as 
    select
    location_id,
    avg_temp_c,
    min_temp_c,
    max_temp_c
from "de_etl_db"."student10"."stg_weather_daily"
where avg_temp_c < min_temp_c or avg_temp_c > max_temp_c
  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_c3c525084f4470d754e943686f3636a1_8486]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_c3c525084f4470d754e943686f3636a1_8486]
  ;')