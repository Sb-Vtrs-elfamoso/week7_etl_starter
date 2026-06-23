# Lab 7.1B starter
# Run this file from the week7_etl_starter repo root.

# %% Imports
from pathlib import Path
from datetime import datetime
import pandas as pd
import uuid


# %% Global variables
WEATHER_BAD_FILE = "data/bad_data/weather_corrections_bad.csv"
WEATHER_GOOD_FILE = "data/sample_weather/weather_good_sample.csv"
LOCATIONS_FILE = "data/reference/locations.csv"
DATE_FILE = "data/reference/date_dimension.csv"
OUTPUT_DIR = "output/7_1B"

# %% Helper functions
def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "data").exists() and (candidate / "dbt_weather").exists():
            return candidate
    raise FileNotFoundError("Could not find repo root. Run this from the week7_etl_starter repo.")


def add_error(existing_value, new_error):
    if pd.isna(existing_value) or existing_value == "":
        return new_error
    return f"{existing_value};{new_error}"

# %% Main
repo = find_repo_root(Path.cwd())

def main() -> None:
    repo = find_repo_root(Path.cwd())
    output_dir = repo / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # %% ETL run metadata
    run_id = str(uuid.uuid4())
    loaded_at = datetime.now().replace(microsecond=0)
    loaded_file_name = repo / WEATHER_BAD_FILE

    print("run_id:", run_id)
    print("loaded_at:", loaded_at)
    print("loaded_file_name:", loaded_file_name)

    # %% TODO 1: read the reference and weather files.
    locations = pd.read_csv(repo / LOCATIONS_FILE)
    date_dimension = pd.read_csv(repo / DATE_FILE)
    good_weather = pd.read_csv(repo / WEATHER_GOOD_FILE)
    raw_weather = pd.read_csv(repo / WEATHER_BAD_FILE)

    print("Weather rows:", len(raw_weather))
    print("Location rows:", len(locations))
    print("Weather columns:", raw_weather.columns.tolist())
    print("Date columns:", date_dimension.columns.tolist())
    print("Location columns:", locations.columns.tolist())

    # %% TODO 2: check the source contract
    required_weather_columns = [
        "location_id", "city", "weather_date", "avg_temp_c", "max_temp_c",
        "min_temp_c", "total_precip_mm", "avg_humidity_pct",
        "avg_wind_speed_kmh", "source_system",
    ]
    
    missing_weather_columns = sorted(set(required_weather_columns) - set(raw_weather.columns))
    
    if missing_weather_columns:
        raise ValueError(f"Missing weather columns: {missing_weather_columns}")
    
    print("Weather source contract check passed.")

    # %% TODO 3: add metadat columns.
    weather = raw_weather.copy()
    weather["run_id"] = run_id
    weather["loaded_at"] = loaded_at
    weather["loaded_file_name"] = loaded_file_name
    weather[["run_id", "loaded_at", "loaded_file_name"]].head()

    # %% TODO 4: convert weather_date to datetime using errors="coerce".
    weather["weather_date"] = pd.to_datetime(weather["weather_date"], errors="coerce")

    # %% TODO 5: convert numeric columns using pd.to_numeric(..., errors="coerce").
    numeric_columns = [
        "avg_temp_c",
        "max_temp_c",
        "min_temp_c",
        "total_precip_mm",
        "avg_humidity_pct",
        "avg_wind_speed_kmh",
    ]
    for column in numeric_columns:
        weather[column] = (
            weather[column]
            .astype("string")
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        weather[column] = pd.to_numeric(weather[column], errors="coerce")
    
    weather[numeric_columns + ["weather_date"]].head()

    # %% TODO 6: add one rejection reason
    weather["rejection_reason"] = ""
    
    def add_rejection_reason(condition: pd.Series, reason: str) -> None:
        current_reason = weather.loc[condition, "rejection_reason"]
        weather.loc[condition, "rejection_reason"] = current_reason.where(
            current_reason.eq(""), current_reason + "; "
        ) + reason

    add_rejection_reason(
        weather["weather_date"].isna(),
        "Missing or invalid weather_date",
    )

    weather.loc[~weather["rejection_reason"].eq(""), ["location_id", "weather_date", "rejection_reason"]]

    # %% TODO 7: add validation checks:
    # - missing location_id
    add_rejection_reason(
        weather["location_id"].isna(),
        "Missing or invalid location id",
    )
    # - missing or invalid weather_date
    add_rejection_reason(
        weather["weather_date"].isna(),
        "Missing or invalid weather_date",
    )
    # - location_id not found in locations.csv
    add_rejection_reason(
        ~weather["location_id"].isin(locations["location_id"]),
        "location_id not found in references",
    )
    # - weather_date not found in date_dimension.csv
    valid_dates = pd.to_datetime(date_dimension["full_date"])
    add_rejection_reason(
        ~weather["weather_date"].isin(valid_dates),
        "weather_date not found in references",
    )
    # - numeric conversion failures
    for col in numeric_columns :
        add_rejection_reason(
            weather[col].isna(),
            f"{col} numeric conversion failure",
        )
    # - negative precipitation
    add_rejection_reason(
        weather["total_precip_mm"] < 0,
        "negative precipitation",
    )
    # - humidity outside 0..100
    add_rejection_reason(
        ~weather["avg_humidity_pct"].between(0, 100),
        "invalid humidity rate",
    )
    # - min_temp_c greater than max_temp_c
    add_rejection_reason(
        weather["min_temp_c"] > weather["max_temp_c"],
        "min temperature superior max temperature",
    )
    # - duplicate location_id + weather_date rows
    add_rejection_reason(
        weather.duplicated(
            subset=["location_id", "weather_date"],
            keep=False,
        ),
        "duplicate location_id + weather_date",
    )
    weather[~weather["rejection_reason"].eq("")]
    
    # %% TODO 8: split accepted and rejected rows.
    accepted_weather = weather[weather["rejection_reason"].eq("")].copy()
    rejected_weather = weather[~weather["rejection_reason"].eq("")].copy()
    
    print("Accepted rows:", len(accepted_weather))
    print("Rejected rows:", len(rejected_weather))

    # %% TODO 9: write output files:
    Path(repo / 'output/lab_7_1b').mkdir(exist_ok=True)
    Path(repo / 'output/lab_7_1b/accepted').mkdir(exist_ok=True)
    Path(repo / 'output/lab_7_1b/rejected').mkdir(exist_ok=True)
    Path(repo / 'output/lab_7_1b/audit').mkdir(exist_ok=True)

    accepted_weather.to_csv(repo / 'output/lab_7_1b/accepted/weather_daily_accepted.csv')
    rejected_weather.to_csv(repo / 'output/lab_7_1b/rejected/weather_daily_rejected.csv')

    summary = weather[~weather["rejection_reason"].eq("")]["rejection_reason"].value_counts()
    summary.to_csv(repo / 'output/lab_7_1b/audit/weather_validation_summary.csv')

    # %% TODO 10: print a short summary.


if __name__ == "__main__":
    main()
# %%
