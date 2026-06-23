
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_84c61aba5bb74533a28bfdfe083e4f12_8238]
   as 
    
    
    

select
    id as unique_field,
    count(*) as n_records

from "de_etl_db"."student10"."dbt_setup_connection_test"
where id is not null
group by id
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
    [student10].[testview_84c61aba5bb74533a28bfdfe083e4f12_8238]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_84c61aba5bb74533a28bfdfe083e4f12_8238]
  ;')