
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_0eff674a193f6627028542db8b1063a7_2446]
   as 
    select
    *
from "de_etl_db"."student10"."mart_weather_daily_by_location"
where country_code is null
  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_0eff674a193f6627028542db8b1063a7_2446]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_0eff674a193f6627028542db8b1063a7_2446]
  ;')