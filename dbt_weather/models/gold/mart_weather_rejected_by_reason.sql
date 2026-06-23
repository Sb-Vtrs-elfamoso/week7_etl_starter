{{ config(materialized='table', tags=['weather', 'gold', 'quality']) }}

select
    rejection_reason,
    COUNT(*) as count
    
from {{ source('student', 'rejected_weather_rows') }}

group by rejection_reason