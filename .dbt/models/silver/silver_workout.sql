{{ config(
    materialized='table'
) }}

WITH raw_data AS (
    SELECT * FROM {{ source('bronze', 'workout_data') }}
)

SELECT DISTINCT
    *,
    TIMESTAMPDIFF(
        MINUTE, 
        STR_TO_DATE(
            REPLACE(REPLACE(REPLACE(REPLACE(LOWER(start_time), 'ene', 'jan'), 'abr', 'apr'), 'ago', 'aug'), 'dic', 'dec'), 
            '%e %b %Y, %H:%i'
        ), 
        STR_TO_DATE(
            REPLACE(REPLACE(REPLACE(REPLACE(LOWER(end_time), 'ene', 'jan'), 'abr', 'apr'), 'ago', 'aug'), 'dic', 'dec'), 
            '%e %b %Y, %H:%i'
        )
    ) AS duracion_minutos
FROM 
    raw_data