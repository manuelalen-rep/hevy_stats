import os


CONFIG = {
    "project_name": "hevy_transformations",
    "profile_name": "hevy_mysql",
    "db_host": "localhost",
    "db_port": 3306,
    "db_user": "root",
    "db_password": "tu_password_segura",
    "schema_target": "SILVER"
}


FOLDERS = [
    "models",
    "models/staging",
    "models/marts",
    "seeds",
    "snapshots",
    "tests",
    "macros",
    "analyses"
]



DBT_PROJECT_YML = f"""
name: '{CONFIG['project_name']}'
version: '1.0.0'
config-version: 2

profile: '{CONFIG['profile_name']}'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:
  - "target"
  - "dbt_packages"

models:
  {CONFIG['project_name']}:
    staging:
      +materialized: view
    marts:
      +materialized: table
"""

PROFILES_YML = f"""
{CONFIG['profile_name']}:
  target: dev
  outputs:
    dev:
      type: mysql
      server: {CONFIG['db_host']}
      port: {CONFIG['db_port']}
      schema: {CONFIG['schema_target']}
      username: {CONFIG['db_user']}
      password: {CONFIG['db_password']}
      threads: 4
"""


STG_WORKOUT_SQL = """
WITH raw_data AS (
    SELECT * FROM {{ source('bronze', 'workout_data') }}
),

cleaned_dates AS (
    SELECT 
        title AS rutina,
        -- Normalización de meses a inglés para el parseo
        STR_TO_DATE(
            REPLACE(REPLACE(REPLACE(REPLACE(LOWER(start_time), 'ene', 'jan'), 'abr', 'apr'), 'ago', 'aug'), 'dic', 'dec'), 
            '%e %b %Y, %H:%i'
        ) AS start_time_ts,
        STR_TO_DATE(
            REPLACE(REPLACE(REPLACE(REPLACE(LOWER(end_time), 'ene', 'jan'), 'abr', 'apr'), 'ago', 'aug'), 'dic', 'dec'), 
            '%e %b %Y, %H:%i'
        ) AS end_time_ts
    FROM raw_data
)

SELECT
    rutina,
    start_time_ts,
    end_time_ts,
    TIMESTAMPDIFF(MINUTE, start_time_ts, end_time_ts) AS duracion_minutos
FROM cleaned_dates
"""

SOURCES_YML = """
version: 2

sources:
  - name: bronze
    database: BRONZE
    tables:
      - name: workout_data
"""


def create_project():
    print(f"🚀 Iniciando scaffolding para el proyecto: {CONFIG['project_name']}")
    

    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_base_path = os.path.abspath(os.path.join(script_dir, "..", ".dbt"))
    
    print(f"🎯 Directorio destino resuelto: {target_base_path}\n")


    os.makedirs(target_base_path, exist_ok=True)
    

    for folder in FOLDERS:
        folder_path = os.path.join(target_base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        

        with open(os.path.join(folder_path, ".gitkeep"), "w") as f:
            pass
        print(f"📁 Creada carpeta: {folder}")


    files_to_create = {
        "dbt_project.yml": DBT_PROJECT_YML.strip(),
        "profiles.yml": PROFILES_YML.strip(),
        "models/staging/stg_workout_data.sql": STG_WORKOUT_SQL.strip(),
        "models/staging/sources.yml": SOURCES_YML.strip()
    }


    for filepath, content in files_to_create.items():

        full_file_path = os.path.join(target_base_path, filepath)
        
        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Creado archivo: {filepath}")

    print(f"\n✅ ¡Scaffolding completado con éxito en '{target_base_path}'!")

if __name__ == "__main__":
    create_project()