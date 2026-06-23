
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_8329e95a5f878eb7c4c9f1f307a92880_9865]
   as 
    
    
    



select total_precip_mm
from "de_etl_db"."student10"."stg_weather_daily"
where total_precip_mm is null



  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_8329e95a5f878eb7c4c9f1f307a92880_9865]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_8329e95a5f878eb7c4c9f1f307a92880_9865]
  ;')