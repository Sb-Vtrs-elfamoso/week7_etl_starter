
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_18838da8510804cf65d48c5bc029de3c_13499]
   as 
    
    
    



select avg_temp_c
from "de_etl_db"."student10"."stg_weather_daily"
where avg_temp_c is null



  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_18838da8510804cf65d48c5bc029de3c_13499]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_18838da8510804cf65d48c5bc029de3c_13499]
  ;')