
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_bc45fbf2496bd90eb3c37ae13eab8416_6530]
   as 
    select
    location_id,
    weather_date,
    count(*) as row_count
from "de_etl_db"."student10"."stg_weather_daily"
group by location_id, weather_date
having count(*) > 1
  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_bc45fbf2496bd90eb3c37ae13eab8416_6530]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_bc45fbf2496bd90eb3c37ae13eab8416_6530]
  ;')