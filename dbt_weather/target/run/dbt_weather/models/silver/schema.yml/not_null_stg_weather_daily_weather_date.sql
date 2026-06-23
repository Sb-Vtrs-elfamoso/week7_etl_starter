
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_19dc2390cd53d56b49dec04757dd0a38_15592]
   as 
    
    
    



select weather_date
from "de_etl_db"."student10"."stg_weather_daily"
where weather_date is null



  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_19dc2390cd53d56b49dec04757dd0a38_15592]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_19dc2390cd53d56b49dec04757dd0a38_15592]
  ;')