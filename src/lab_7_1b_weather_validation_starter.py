from pathlib import Path
import pandas as pd

# Lab 7.1B starter
# Run this file from the week7_etl_starter repo root.

WEATHER_BAD_FILE = "data/bad_data/weather_corrections_bad.csv"
WEATHER_GOOD_FILE = "data/sample_weather/weather_good_sample.csv"
LOCATIONS_FILE = "data/reference/locations.csv"
DATE_FILE = "data/reference/date_dimension.csv"
OUTPUT_DIR = "output/7_1B"


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


def main() -> None:
    repo = find_repo_root(Path.cwd())
    output_dir = repo / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # TODO 1: read the reference and weather files.
    # locations = ...
    # date_dimension = ...
    # good_weather = ...
    # raw_weather = ...

    # TODO 2: print row counts for good_weather and raw_weather.

    # TODO 3: add source_file and source_row_number to raw_weather.

    # TODO 4: convert weather_date to datetime using errors="coerce".

    # TODO 5: convert numeric columns using pd.to_numeric(..., errors="coerce").
    numeric_columns = [
        "avg_temp_c",
        "max_temp_c",
        "min_temp_c",
        "total_precip_mm",
        "avg_humidity_pct",
        "avg_wind_speed_kmh",
    ]

    # TODO 6: create an error_reasons column. Start with an empty string.

    # TODO 7: add validation checks:
    # - missing location_id
    # - missing or invalid weather_date
    # - location_id not found in locations.csv
    # - weather_date not found in date_dimension.csv
    # - numeric conversion failures
    # - negative precipitation
    # - humidity outside 0..100
    # - min_temp_c greater than max_temp_c
    # - duplicate location_id + weather_date rows

    # TODO 8: split accepted and rejected rows.
    # accepted = ...
    # rejected = ...

    # TODO 9: write output files:
    # output/7_1B/weather_accepted.csv
    # output/7_1B/weather_rejected.csv
    # output/7_1B/weather_validation_summary.csv

    # TODO 10: print a short summary.


if __name__ == "__main__":
    main()