
    
    

select
    id as unique_field,
    count(*) as n_records

from "de_etl_db"."student10"."dbt_setup_connection_test"
where id is not null
group by id
having count(*) > 1


