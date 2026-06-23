
    
    -- Create target schema if it does not
  USE [de_etl_db];
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'student10')
  BEGIN
    EXEC('CREATE SCHEMA [student10]')
  END

  

  
  EXEC('create view 
    [student10].[testview_1aa2a4772ffb56c97de3e2dd8f18a029_3291]
   as 
    
    
    



select id
from "de_etl_db"."student10"."dbt_setup_connection_test"
where id is null



  ;')
  select
    
    count(*) as failures,
    case when count(*) != 0
      then 'true' else 'false' end as should_warn,
    case when count(*) != 0
      then 'true' else 'false' end as should_error
  from (
    select * from 
    [student10].[testview_1aa2a4772ffb56c97de3e2dd8f18a029_3291]
  
  ) dbt_internal_test;

  EXEC('drop view 
    [student10].[testview_1aa2a4772ffb56c97de3e2dd8f18a029_3291]
  ;')