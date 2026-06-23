

select
    rejection_reason,
    COUNT(*) as count
    
from "de_etl_db"."student10"."rejected_weather_rows"

group by rejection_reason