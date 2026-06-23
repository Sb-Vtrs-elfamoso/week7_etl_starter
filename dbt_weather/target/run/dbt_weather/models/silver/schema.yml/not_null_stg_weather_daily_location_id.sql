
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_905ff0f726e90c224e0b867c9fc98c1c_10581]
   as 
    
    
    



select location_id
from "de_etl_db"."student10"."stg_weather_daily"
where location_id is null



  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_905ff0f726e90c224e0b867c9fc98c1c_10581]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_905ff0f726e90c224e0b867c9fc98c1c_10581]
  ;')