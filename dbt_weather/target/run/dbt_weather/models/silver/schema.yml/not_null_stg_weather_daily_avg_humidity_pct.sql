
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_ab9ff40042ef055ab56aa3351c5824fd_14635]
   as 
    
    
    



select avg_humidity_pct
from "de_etl_db"."student10"."stg_weather_daily"
where avg_humidity_pct is null



  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_ab9ff40042ef055ab56aa3351c5824fd_14635]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_ab9ff40042ef055ab56aa3351c5824fd_14635]
  ;')