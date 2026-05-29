{{ config(
    materialized='view',
    schema='GOLD'
) }}

WITH parsed AS (
    SELECT *,
        STR_TO_DATE(
            REPLACE(REPLACE(REPLACE(REPLACE(LOWER(start_time),
                'ene','jan'),'abr','apr'),'ago','aug'),'dic','dec'),
            '%e %b %Y, %H:%i'
        ) AS start_ts
    FROM {{ source('silver', 'silver_workout') }}
)

SELECT
    '0001' AS user_id,
    title AS routine_name,
    start_ts AS workout_start,
    end_time AS workout_end,
    duracion_minutos AS duration_min,
    DATE(start_ts) AS workout_date,
    YEAR(start_ts) AS year,
    MONTH(start_ts) AS month,
    WEEK(start_ts) AS week,
    DAYOFWEEK(start_ts) AS weekday_num,
    DAYNAME(start_ts) AS weekday_name,
    CASE
        WHEN HOUR(start_ts) < 12 THEN 'morning'
        WHEN HOUR(start_ts) < 17 THEN 'afternoon'
        ELSE 'evening'
    END AS time_of_day,
    COUNT(DISTINCT exercise_title) AS total_exercises,
    COUNT(*) AS total_sets,
    SUM(CASE WHEN set_type = 'normal' THEN 1 ELSE 0 END) AS working_sets,
    SUM(COALESCE(reps, 0)) AS total_reps,
    ROUND(SUM(COALESCE(weight_kg, 0) * COALESCE(reps, 0)), 1) AS total_volume_kg,
    ROUND(AVG(CASE WHEN weight_kg > 0 THEN weight_kg END), 1) AS avg_weight_kg,
    MAX(weight_kg) AS max_weight_kg,
    ROUND(SUM(COALESCE(weight_kg, 0) * COALESCE(reps, 0)) / NULLIF(duracion_minutos, 0), 1) AS volume_per_minute,
    _loaded_at
FROM parsed
GROUP BY
    title, start_ts, end_time, duracion_minutos, _loaded_at
ORDER BY workout_start DESC
