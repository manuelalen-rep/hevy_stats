import os
import sys
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, types as sqltypes

load_dotenv()

REQUIRED_ENV_VARS = {
    "CLOUDFLARE_ACCOUNT_ID": "Account ID de Cloudflare",
    "R2_ACCESS_KEY_ID": "Access Key ID de R2",
    "R2_SECRET_ACCESS_KEY": "Secret Access Key de R2",
    "MYSQL_HOST": "Host de MySQL",
    "MYSQL_PORT": "Puerto de MySQL",
    "MYSQL_DATABASE": "Base de datos destino (bronze)",
    "MYSQL_USER": "Usuario de MySQL",
    "MYSQL_PASSWORD": "Contraseña de MySQL",
}

missing = []
for var, description in REQUIRED_ENV_VARS.items():
    value = os.getenv(var)
    if not value:
        missing.append(f"  - {var} ({description})")

if missing:
    print("ERROR: Faltan las siguientes variables de entorno en .env:")
    print("\n".join(missing))
    sys.exit(1)

try:
    import s3fs
except ImportError:
    print("ERROR: Falta la librería 's3fs'. Instálala con: pip install s3fs")
    sys.exit(1)

# ── Parámetros ──────────────────────────────────────────
account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
bucket_name = "raw"
file_name = "hevy/workout_data.csv"
table_name = "workout_data"

mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST")
mysql_port = os.getenv("MYSQL_PORT")
mysql_database = os.getenv("MYSQL_DATABASE")

r2_url = f"s3://{bucket_name}/{file_name}"
endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

# ── 1. Extraer CSV desde R2 ──────────────────────────────
print(f"1. Leyendo '{file_name}' desde R2...")
try:
    df = pd.read_csv(
        r2_url,
        storage_options={
            "key": os.getenv("R2_ACCESS_KEY_ID"),
            "secret": os.getenv("R2_SECRET_ACCESS_KEY"),
            "client_kwargs": {
                "endpoint_url": endpoint_url,
                "region_name": "auto",
            },
            "config_kwargs": {
                "signature_version": "s3v4",
            },
        },
        encoding="utf-8",
        on_bad_lines="warn",
    )
except Exception as e:
    print(f"ERROR al leer CSV desde R2: {e}")
    sys.exit(1)

print(f"   Filas: {len(df):,} | Columnas: {len(df.columns)}")
print(f"   Memoria: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

# ── 2. Conectar a MySQL y crear DB bronze si no existe ───
print(f"2. Conectando a MySQL...")
try:
    engine_admin = create_engine(
        f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}",
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    with engine_admin.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{mysql_database}`"))
        conn.commit()
    engine_admin.dispose()
    print(f"   Base de datos '{mysql_database}' lista.")

    engine = create_engine(
        f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}",
        pool_pre_ping=True,
        pool_recycle=3600,
    )
except Exception as e:
    print(f"ERROR al conectar a MySQL: {e}")
    sys.exit(1)

# ── 3. Mapear tipos pandas → MySQL y agregar columna de auditoría ──
print(f"3. Preparando tabla '{table_name}'...")

PANDAS_TO_MYSQL = {
    "int64": sqltypes.BIGINT,
    "Int64": sqltypes.BIGINT,
    "int32": sqltypes.INTEGER,
    "Int32": sqltypes.INTEGER,
    "float64": sqltypes.DOUBLE,
    "Float64": sqltypes.DOUBLE,
    "float32": sqltypes.FLOAT,
    "Float32": sqltypes.FLOAT,
    "object": sqltypes.TEXT,
    "bool": sqltypes.BOOLEAN,
    "datetime64[ns]": sqltypes.DATETIME,
    "datetime64[us]": sqltypes.DATETIME,
    "datetime64": sqltypes.DATETIME,
}

dtype_dict = {
    col: PANDAS_TO_MYSQL.get(str(dt), sqltypes.TEXT)
    for col, dt in df.dtypes.items()
}

df["_loaded_at"] = datetime.now(timezone.utc)

# ── 4. Insertar a MySQL (reemplaza la tabla completa) ──
print(f"4. Insertando {len(df):,} filas en '{mysql_database}.{table_name}'...")
try:
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        dtype=dtype_dict,
        method="multi",
        chunksize=500,
    )
except Exception as e:
    print(f"ERROR al insertar datos en MySQL: {e}")
    engine.dispose()
    sys.exit(1)

engine.dispose()
print(f"   Insercion completada.")
print(f"\nResumen:")
print(f"   - Origen:  R2 ({bucket_name}/{file_name})")
print(f"   - Destino: MySQL {mysql_host}:{mysql_port}/{mysql_database}.{table_name}")
print(f"   - Filas:   {len(df):,}")
print(f"   - Columnas: {len(df.columns)}")
print(f"   - Ingesta:  {df['_loaded_at'].iloc[0]}")
