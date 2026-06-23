
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_53e370067b72da6a89319a04b74e18ba_3616]
   as 
    select
    location_id,
    avg_humidity_pct
from "de_etl_db"."student10"."stg_weather_daily"
where avg_humidity_pct < 0 or avg_humidity_pct > 100
  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_53e370067b72da6a89319a04b74e18ba_3616]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_53e370067b72da6a89319a04b74e18ba_3616]
  ;')