
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_66636245d5fe2d534afc9df51d340274_13792]
   as 
    select
    location_id,
    weather_date,
    total_precip_mm
from "de_etl_db"."student10"."stg_weather_daily"
where total_precip_mm < 0
  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_66636245d5fe2d534afc9df51d340274_13792]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_66636245d5fe2d534afc9df51d340274_13792]
  ;')