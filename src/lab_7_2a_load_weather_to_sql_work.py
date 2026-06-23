# Lab 7 2A
# Loading validated weather data to SQL

# %% Warm-up 1 - Project setup and imports

from pathlib import Path
from datetime import datetime
import os
import uuid
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

PROJECT = Path.cwd()
OUTPUT_71B = PROJECT / "output" / "lab_7_1b"
OUTPUT_72A = PROJECT / "output" / "lab_7_2a"
OUTPUT_72A.mkdir(parents=True, exist_ok=True)

ACCEPTED_FILE = OUTPUT_71B / "accepted" / "weather_daily_accepted.csv"
REJECTED_FILE = OUTPUT_71B / "rejected" / "weather_daily_rejected.csv"
SUMMARY_FILE = OUTPUT_71B / "audit" / "weather_validation_summary.csv"
RAW_WEATHER_FILE = PROJECT / "data" / "bad_data" / "weather_corrections_bad.csv"

print("Project:", PROJECT)
print("Lab 7.1B output folder exists:", OUTPUT_71B.exists())

# %% Warm-up 2 - Verify expected input files
expected_files = [ACCEPTED_FILE, REJECTED_FILE, SUMMARY_FILE, RAW_WEATHER_FILE]
missing_files = [str(path) for path in expected_files if not path.exists()]

if missing_files:
    raise FileNotFoundError("Missing required files: " + ", ".join(missing_files))

print("All required files exist.")

# %% Warm-up 3 - Load Azure SQL settings from .env
load_dotenv()

server = os.getenv("AZURE_SQL_SERVER")
database = os.getenv("AZURE_SQL_DATABASE")
user = os.getenv("AZURE_SQL_USER")
password = os.getenv("AZURE_SQL_PASSWORD")
schema_name = os.getenv("AZURE_SQL_SCHEMA")

required_settings = {
    "AZURE_SQL_SERVER": server,
    "AZURE_SQL_DATABASE": database,
    "AZURE_SQL_USER": user,
    "AZURE_SQL_PASSWORD": password,
    "AZURE_SQL_SCHEMA": schema_name,
}

missing_settings = [name for name, value in required_settings.items() if not value]
if missing_settings:
    raise ValueError("Missing .env settings: " + ", ".join(missing_settings))

print("Database:", database)
print("Schema:", schema_name)

# %% Warm-up 4 - Create SQLAlchemy engine
sql_password = os.getenv("SQL_PASSWORD")
sql_uid = os.getenv("SQL_UID")
connection_url = URL.create(
    "mssql+pyodbc",
    username=user,
    password=password,
    host=server,
    port=1433,
    database=database,
    query={
        "driver": "ODBC Driver 17 for SQL Server",
        "UID": sql_uid,
        "PWD": sql_password,
        "TrustServerCertificate": "no",
    },
)

engine = create_engine(connection_url, fast_executemany=True)
print("Engine created.")

# %% Warm-up 5 - Test the connection
with engine.connect() as conn:
    row = conn.execute(text("SELECT DB_NAME() AS database_name")).fetchone()
    print(row)


# %% Warm-up 6 - Read the already validated output files
accepted = pd.read_csv(ACCEPTED_FILE)
rejected = pd.read_csv(REJECTED_FILE)
summary = pd.read_csv(SUMMARY_FILE)
raw_weather = pd.read_csv(RAW_WEATHER_FILE)

print("accepted rows:", len(accepted))
print("rejected rows:", len(rejected))
print("summary rows:", len(summary))
print("raw weather rows:", len(raw_weather))

# %% Warm-up 7 - Create a small connection test table
connection_test = pd.DataFrame({
    "test_name": ["lab_7_2a_connection"],
    "schema_name": [schema_name],
    "row_count": [1],
})

connection_test.to_sql(
    name="lab_7_2a_connection_test",
    con=engine,
    schema=schema_name,
    if_exists="replace",
    index=False,
)

print("Connection test table written.")

# %% Warm-up 8 - Load one real output table
accepted.to_sql(
    name="silver_weather_daily_clean",
    con=engine,
    schema=schema_name,
    if_exists="replace",
    index=False,
)

print("silver_weather_daily_clean written:", len(accepted), "rows")

# %% Warm-up 9 - Verify table row count from Azure SQL
with engine.connect() as conn:
    sql = text(f"SELECT COUNT(*) AS row_count FROM {schema_name}.silver_weather_daily_clean")
    row_count = conn.execute(sql).scalar_one()

print("Rows in Azure SQL table:", row_count)

# %% Warm-up 10 - Create a reusable load helper
def replace_table(df: pd.DataFrame, table_name: str) -> None:
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema_name,
        if_exists="replace",
        index=False,
    )
    print(f"Wrote {schema_name}.{table_name}: {len(df)} rows")

# %% Base Tasks
replace_table(raw_weather, "bronze_weather_api_raw")
replace_table(accepted, "silver_weather_daily_clean")
replace_table(rejected, "rejected_weather_rows")
replace_table(summary, "weather_validation_summary")

summary_rows = []

with engine.connect() as conn:
    for table_name in ["bronze_weather_api_raw", "silver_weather_daily_clean", "rejected_weather_rows", "weather_validation_summary"]:
        sql = text(f"SELECT COUNT(*) AS row_count FROM {schema_name}.{table_name}")
        row_count = conn.execute(sql).scalar_one()

        print("Rows in Azure SQL table", table_name, ':', row_count)
        summary_rows.append(
            {
                "table_name": table_name,
                "row_count": row_count,
            }
        )

load_summary = pd.DataFrame(summary_rows)
print(load_summary)

load_summary.to_csv(OUTPUT_72A / 'weather_sql_load_summary.csv')

# %% Practice tasks
with engine.connect() as conn:
    sql = text(f"SELECT TOP 10 * FROM {schema_name}.silver_weather_daily_clean")
    silver_head = conn.execute(sql)
    for row in silver_head:
        print(row)

with engine.connect() as conn:
    sql = text(f"SELECT rejection_reason, COUNT(*) as count FROM {schema_name}.rejected_weather_rows GROUP BY rejection_reason")
    rejections = conn.execute(sql)
    for row in rejections:
        print(row)

with engine.connect() as conn:
    sql = text(f"SELECT TOP 1 MIN(weather_date) OVER() as start_date, MAX(weather_date) OVER() as end_date FROM {schema_name}.silver_weather_daily_clean")
    date_range = conn.execute(sql)
    for row in date_range:
        print(row)

tables_list = []
sql = text(
    f"SELECT TABLE_NAME "
    f"FROM INFORMATION_SCHEMA.TABLES "
    f"WHERE TABLE_SCHEMA = '{schema_name}'"
)

with engine.connect() as conn:
    tables = conn.execute(sql)
    for row in tables:
        print(row)
        tables_list.append(row[0])

# %% Extras
load_log = {
    'process_name' : 'Bronze / Silver Loading',
    'loaded_to_sql_at' : datetime.now().replace(microsecond=0),
    'bronze_row_count' : load_summary['row_count'].iloc[0],
    'silver_row_count' : load_summary['row_count'].iloc[1],
    'rejected_row_count' : load_summary['row_count'].iloc[2],
    'summary_row_count' : load_summary['row_count'].iloc[3],
    'status' : 'Successfully transfered',
    'notes' : 'Done by Sébastien Vouters on my Mac Mini'
}
load_log = pd.DataFrame([load_log])
print(load_log)
replace_table(load_log, "etl_load_log")

