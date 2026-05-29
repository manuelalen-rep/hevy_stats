-- ============================================================
-- Índices recomendados para SILVER.silver_workout
-- Mejoran el rendimiento de la vista gold.v_gold_workout_summary
-- ============================================================

-- Índice para filtros por fecha (WHERE, GROUP BY, ORDER BY)
ALTER TABLE SILVER.silver_workout
    ADD INDEX idx_silver_start (start_time(20));

-- Índice para agrupaciones por rutina (GROUP BY title)
ALTER TABLE SILVER.silver_workout
    ADD INDEX idx_silver_title (title(50));

-- Índice para filtros y agrupaciones por ejercicio
ALTER TABLE SILVER.silver_workout
    ADD INDEX idx_silver_exercise (exercise_title(50));
