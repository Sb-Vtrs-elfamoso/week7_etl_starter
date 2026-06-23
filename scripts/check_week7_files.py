from pathlib import Path
import pandas as pd

EXPECTED_FILES = [
    ("data/reference/locations.csv", "Location reference / later dim_location"),
    ("data/reference/date_dimension.csv", "Date reference / later dim_date"),
    ("data/reference/country_indicators.csv", "Annual country indicators / later enrichment source"),
    ("data/sample_weather/weather_good_sample.csv", "Good weather sample / clean comparison file"),
    ("data/bad_data/weather_corrections_bad.csv", "Imperfect incoming weather file for validation practice"),
]


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "data").exists() and (candidate / "dbt_weather").exists():
            return candidate
    raise FileNotFoundError("Could not find repo root. Run this from the week7_etl_starter repo.")


def main() -> None:
    repo = find_repo_root(Path.cwd())
    print(f"Repo root: {repo}")
    print()

    rows = []
    for relative_path, role in EXPECTED_FILES:
        path = repo / relative_path
        exists = path.exists()
        if exists:
            df = pd.read_csv(path)
            rows.append({
                "file": relative_path,
                "exists": exists,
                "rows": len(df),
                "columns": len(df.columns),
                "role": role,
            })
        else:
            rows.append({
                "file": relative_path,
                "exists": exists,
                "rows": None,
                "columns": None,
                "role": role,
            })

    summary = pd.DataFrame(rows)
    print(summary.to_string(index=False))

    print("\nExpected row counts for current training data:")
    print("locations.csv: 6")
    print("date_dimension.csv: 31")
    print("country_indicators.csv: 18")
    print("weather_good_sample.csv: 186")
    print("weather_corrections_bad.csv: 187")


if __name__ == "__main__":
    main()