
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_a781f23417335ba6a87cbe8ec5baa175_12497]
   as 
    
    
    



select location_id
from "de_etl_db"."student10"."mart_weather_daily_by_location"
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
    [student10].[testview_a781f23417335ba6a87cbe8ec5baa175_12497]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_a781f23417335ba6a87cbe8ec5baa175_12497]
  ;')