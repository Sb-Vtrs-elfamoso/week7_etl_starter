

select
    'accepted_weather_rows' as metric_name,
    count(*) as metric_value
from "de_etl_db"."student10"."stg_weather_daily"

union all

select
    'rejected_weather_rows' as metric_name,
    count(*) as metric_value
from "de_etl_db"."student10"."rejected_weather_rows"

union all

select
    'gold_weather_rows' as metric_name,
    count(*) as metric_value
from "de_etl_db"."student10"."mart_weather_daily_by_location"