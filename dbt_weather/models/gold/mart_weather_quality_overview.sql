{{ config(materialized='table', tags=['weather', 'gold', 'quality']) }}

select
    'accepted_weather_rows' as metric_name,
    count(*) as metric_value
from {{ ref('stg_weather_daily') }}

union all

select
    'rejected_weather_rows' as metric_name,
    count(*) as metric_value
from {{ source('student', 'rejected_weather_rows') }}

union all

select
    'gold_weather_rows' as metric_name,
    count(*) as metric_value
from {{ ref('mart_weather_daily_by_location') }}