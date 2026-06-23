
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_8ab42ea4e1c681c2eb6fa711cc251fdd_2009]
   as 
    
    
    

select
    location_id as unique_field,
    count(*) as n_records

from "de_etl_db"."student10"."stg_locations"
where location_id is not null
group by location_id
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
    [student10].[testview_8ab42ea4e1c681c2eb6fa711cc251fdd_2009]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_8ab42ea4e1c681c2eb6fa711cc251fdd_2009]
  ;')