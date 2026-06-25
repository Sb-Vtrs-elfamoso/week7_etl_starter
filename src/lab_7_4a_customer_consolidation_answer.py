"""
Lab 7.4A answer - Customer consolidation and survivorship rules

This answer file includes:
- Required base tasks 1-10
- Practice tasks P1-P5
- Extras E1-E4
- Advanced extras A1-A4

Run from the repository root:
    python src/lab_7_4a_customer_consolidation_answer_full.py
"""

from pathlib import Path
import pandas as pd


# -----------------------------------------------------------------------------
# Base setup
# -----------------------------------------------------------------------------

BASE_DIR = Path.cwd()
INPUT_DIR = BASE_DIR / "data" / "customer_sources"
OUTPUT_DIR = BASE_DIR / "output" / "lab_7_4a"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CRM_FILE = INPUT_DIR / "crm_customers.csv"
WEBSHOP_FILE = INPUT_DIR / "webshop_customers.csv"


def normalize_email(series: pd.Series) -> pd.Series:
    """Trim spaces, lowercase, and turn empty strings into missing values."""
    return series.astype("string").str.strip().str.lower().replace("", pd.NA)


def normalize_phone(series: pd.Series) -> pd.Series:
    """Simple phone normalization for the lab: remove spaces and trim."""
    return (
        series.astype("string")
        .str.replace(" ", "", regex=False)
        .str.strip()
        .replace("", pd.NA)
    )


def latest_non_null(group: pd.DataFrame, column: str):
    """
    Return the newest non-null value from a matched customer group.

    Used for fields where the lab rule is:
        use the latest non-null value by source_updated_at
    """
    rows = group[group[column].notna()].sort_values("source_updated_at", ascending=False)

    if rows.empty:
        return pd.NA

    return rows.iloc[0][column]


def crm_first_then_latest(group: pd.DataFrame, column: str):
    """
    Return a value using this lab's priority rule:
        1. Prefer CRM when CRM has a value.
        2. If CRM does not have a value, use the latest non-null value.
    """
    rows = group[group[column].notna()].copy()

    if rows.empty:
        return pd.NA

    rows = rows.sort_values(
        ["source_priority", "source_updated_at"],
        ascending=[True, False],
    )

    return rows.iloc[0][column]


def create_standardized_sources(crm: pd.DataFrame, webshop: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create standardized CRM and webshop DataFrames with the same column names."""
    country_map = {
        "Finland": "FI",
        "UK": "GB",
        "Italy": "IT",
        "Sweden": "SE",
        "Denmark": "DK",
        "Norway": "NO",
    }

    crm_std = pd.DataFrame({
        "source_system": "crm",
        "source_customer_id": crm["crm_customer_id"],
        "first_name": crm["first_name"].astype("string").str.strip(),
        "last_name": crm["last_name"].astype("string").str.strip(),
        "email": crm["email"].astype("string").str.strip(),
        "phone": normalize_phone(crm["phone"]),
        "address": crm["street_address"].astype("string").str.strip().replace("", pd.NA),
        "city": crm["city"].astype("string").str.strip(),
        "country_code": crm["country"].map(country_map).fillna(crm["country"]),
        "marketing_consent": pd.NA,
        "source_updated_at": pd.to_datetime(crm["updated_at"]),
    })

    name_parts = webshop["full_name"].astype("string").str.strip().str.split(" ")

    webshop_std = pd.DataFrame({
        "source_system": "webshop",
        "source_customer_id": webshop["webshop_customer_id"],
        "first_name": name_parts.str[0],
        "last_name": name_parts.str[-1],
        "email": webshop["email"].astype("string").str.strip(),
        "phone": normalize_phone(webshop["mobile_phone"]),
        "address": webshop["address"].astype("string").str.strip().replace("", pd.NA),
        "city": webshop["city"].astype("string").str.strip(),
        "country_code": webshop["country_code"].astype("string").str.strip(),
        "marketing_consent": (
            webshop["marketing_consent"]
            .astype("string")
            .str.lower()
            .map({"true": True, "false": False})
        ),
        "source_updated_at": pd.to_datetime(webshop["updated_at"]),
    })

    return crm_std, webshop_std


def create_conflicts(matchable: pd.DataFrame, conflict_fields: list[str]) -> pd.DataFrame:
    """Create one conflict row when a matched email group has multiple different values for a field."""
    conflict_rows = []

    for email, group in matchable.groupby("normalized_email"):
        for field in conflict_fields:
            distinct_values = sorted({str(v) for v in group[field].dropna().unique()})

            if len(distinct_values) > 1:
                conflict_rows.append({
                    "normalized_email": email,
                    "field_name": field,
                    "distinct_value_count": len(distinct_values),
                    "values_found": " | ".join(distinct_values),
                })

    return pd.DataFrame(conflict_rows)


def create_golden_customers(matchable: pd.DataFrame) -> pd.DataFrame:
    """Apply survivorship rules and create one golden customer row per normalized email."""
    survivors = []

    for email, group in matchable.groupby("normalized_email"):
        ordered = group.sort_values(
            ["completeness_score", "source_priority", "source_updated_at"],
            ascending=[False, True, False],
        )

        base = ordered.iloc[0]

        row = {
            "customer_business_key": email,
            "first_name": crm_first_then_latest(group, "first_name"),
            "last_name": crm_first_then_latest(group, "last_name"),
            "email": email,
            "phone": crm_first_then_latest(group, "phone"),
            "address": latest_non_null(group, "address"),
            "city": latest_non_null(group, "city"),
            "country_code": latest_non_null(group, "country_code"),
            "marketing_consent": latest_non_null(group, "marketing_consent"),
            "completeness_score": int(ordered["completeness_score"].max()),
            "source_row_count": len(group),
            "base_source_customer_id": base["source_customer_id"],
        }

        survivors.append(row)

    return (
        pd.DataFrame(survivors)
        .sort_values("customer_business_key")
        .reset_index(drop=True)
    )


# -----------------------------------------------------------------------------
# Required base tasks
# -----------------------------------------------------------------------------

# Task 1 - Read CRM and webshop source files
crm = pd.read_csv(CRM_FILE, dtype="string")
webshop = pd.read_csv(WEBSHOP_FILE, dtype="string")

print("Task 1 - Source row counts and columns")
print("CRM rows:", len(crm))
print("CRM columns:", crm.columns.tolist())
print("Webshop rows:", len(webshop))
print("Webshop columns:", webshop.columns.tolist())
print()


# Task 2 - Create crm_std with common columns
# Task 3 - Create webshop_std with same common columns
crm_std, webshop_std = create_standardized_sources(crm, webshop)

print("Task 2 - crm_std preview")
print(crm_std.head())
print()

print("Task 3 - webshop_std preview")
print(webshop_std.head())
print()


# Task 4 - Combine crm_std and webshop_std into candidates
candidates = pd.concat([crm_std, webshop_std], ignore_index=True)

print("Task 4 - Combined candidate rows:", len(candidates))
print()


# Task 5 - Create normalized_email and split missing-email rows to review
candidates["normalized_email"] = normalize_email(candidates["email"])

missing_email_review = candidates[candidates["normalized_email"].isna()].copy()
matchable = candidates[candidates["normalized_email"].notna()].copy()

print("Task 5 - Missing email review rows:", len(missing_email_review))
print("Task 5 - Matchable rows:", len(matchable))
print()


# Task 6 - Add completeness_score and source_priority
score_columns = [
    "first_name",
    "last_name",
    "email",
    "phone",
    "address",
    "city",
    "country_code",
    "marketing_consent",
    "source_updated_at",
]

candidates["source_priority"] = candidates["source_system"].map({"crm": 1, "webshop": 2})
candidates["completeness_score"] = candidates[score_columns].notna().sum(axis=1)

# Recreate matchable and missing_email_review so they include the new columns.
missing_email_review = candidates[candidates["normalized_email"].isna()].copy()
matchable = candidates[candidates["normalized_email"].notna()].copy()

print("Task 6 - Completeness score preview")
print(matchable[["source_system", "source_customer_id", "normalized_email", "completeness_score", "source_priority"]].head())
print()


# Task 7 - Create customer_match_audit
# Version A: simple step-by-step version.
# This avoids using a lambda inside groupby aggregation.
match_audit_base = (
    matchable.groupby("normalized_email")
    .agg(
        source_row_count=("source_customer_id", "count"),
        max_completeness_score=("completeness_score", "max"),
        newest_source_updated_at=("source_updated_at", "max"),
    )
    .reset_index()
)

# Create source_systems separately in easier steps.
source_system_rows = (
    matchable[["normalized_email", "source_system"]]
    .drop_duplicates()
    .sort_values(["normalized_email", "source_system"])
)

source_systems = (
    source_system_rows.groupby("normalized_email")["source_system"]
    .agg(",".join)
    .reset_index(name="source_systems")
)

match_audit = match_audit_base.merge(
    source_systems,
    on="normalized_email",
    how="left",
)

match_audit = match_audit[
    [
        "normalized_email",
        "source_row_count",
        "source_systems",
        "max_completeness_score",
        "newest_source_updated_at",
    ]
]

# Task 7 - Alternative Version B: compact version using lambda.
# This is shorter but more advanced.
match_audit_compact = (
    matchable.groupby("normalized_email")
    .agg(
        source_row_count=("source_customer_id", "count"),
        source_systems=("source_system", lambda s: ",".join(sorted(set(s)))),
        max_completeness_score=("completeness_score", "max"),
        newest_source_updated_at=("source_updated_at", "max"),
    )
    .reset_index()
)

print("Task 7 - Match audit preview, simple version")
print(match_audit.head())
print()


# Task 8 - Create customer_conflicts
conflict_fields = ["phone", "address", "city", "country_code", "marketing_consent"]

customer_conflicts = create_conflicts(matchable, conflict_fields)

print("Task 8 - Conflict rows:", len(customer_conflicts))
print(customer_conflicts.head())
print()


# Task 9 - Apply survivorship rules to create customer_golden
customer_golden = create_golden_customers(matchable)

print("Task 9 - Golden customer rows:", len(customer_golden))
print(customer_golden.head())
print()


# Task 10 - Write required outputs under output/lab_7_4a/
summary = pd.DataFrame([
    {"metric_name": "crm_source_rows", "metric_value": len(crm)},
    {"metric_name": "webshop_source_rows", "metric_value": len(webshop)},
    {"metric_name": "combined_candidate_rows", "metric_value": len(candidates)},
    {"metric_name": "missing_email_review_rows", "metric_value": len(missing_email_review)},
    {"metric_name": "golden_customer_rows", "metric_value": len(customer_golden)},
    {"metric_name": "matched_email_groups", "metric_value": int((match_audit["source_row_count"] > 1).sum())},
    {"metric_name": "conflict_rows", "metric_value": len(customer_conflicts)},
])

customer_golden.to_csv(OUTPUT_DIR / "customer_golden.csv", index=False)
customer_conflicts.to_csv(OUTPUT_DIR / "customer_conflicts.csv", index=False)
match_audit.to_csv(OUTPUT_DIR / "customer_match_audit.csv", index=False)
missing_email_review.to_csv(OUTPUT_DIR / "customer_missing_email_review.csv", index=False)
summary.to_csv(OUTPUT_DIR / "customer_consolidation_summary.csv", index=False)

print("Task 10 - Required outputs written")
print(summary)
print()


# -----------------------------------------------------------------------------
# Expected result checks
# -----------------------------------------------------------------------------

print("Expected result checks")
print("CRM source rows:", len(crm))
print("Webshop source rows:", len(webshop))
print("Combined candidate rows:", len(candidates))
print("Missing-email review rows:", len(missing_email_review))
print("Golden customer rows:", len(customer_golden))
print("Matched email groups:", int((match_audit["source_row_count"] > 1).sum()))
print("Conflict rows:", len(customer_conflicts))
print()


# -----------------------------------------------------------------------------
# Practice tasks
# -----------------------------------------------------------------------------

# P1 - Print duplicate groups where source_row_count is greater than 1
duplicate_groups = match_audit[match_audit["source_row_count"] > 1].copy()

print("P1 - Duplicate / matched email groups")
print(duplicate_groups)
print()


# P2 - Display all candidate rows for Anna and explain the golden result
anna_rows = candidates[
    candidates["normalized_email"].eq("anna.virtanen@example.com")
].copy()

anna_golden = customer_golden[
    customer_golden["customer_business_key"].eq("anna.virtanen@example.com")
].copy()

print("P2 - Candidate rows for anna.virtanen@example.com")
print(anna_rows[
    [
        "source_system",
        "source_customer_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "city",
        "country_code",
        "marketing_consent",
        "source_updated_at",
        "completeness_score",
        "source_priority",
    ]
])
print()
print("P2 - Golden row for Anna")
print(anna_golden)
print()

print("P2 explanation:")
print("- CRM is preferred for first_name, last_name and phone when CRM has a value.")
print("- Address, city, country_code and marketing_consent use the latest non-null value.")
print("- Conflicts are still written separately; they are not hidden.")
print()


# P3 - Sort customer_conflicts by normalized_email and field_name before writing
customer_conflicts = customer_conflicts.sort_values(
    ["normalized_email", "field_name"]
).reset_index(drop=True)

customer_conflicts.to_csv(
    OUTPUT_DIR / "customer_conflicts.csv",
    index=False,
)

print("P3 - Sorted customer_conflicts written")
print()


# P4 - Add summary metric for customers found in both CRM and webshop
customers_in_both_systems = match_audit[
    match_audit["source_systems"].eq("crm,webshop")
].copy()

both_systems_metric = pd.DataFrame([
    {
        "metric_name": "customers_found_in_both_crm_and_webshop",
        "metric_value": len(customers_in_both_systems),
    }
])

summary = pd.concat([summary, both_systems_metric], ignore_index=True)

summary.to_csv(
    OUTPUT_DIR / "customer_consolidation_summary.csv",
    index=False,
)

print("P4 - Added customers_found_in_both_crm_and_webshop metric")
print(summary)
print()


# P5 - Display first 10 golden customers with selected columns
print("P5 - First 10 golden customers")
print(
    customer_golden[
        [
            "customer_business_key",
            "first_name",
            "last_name",
            "phone",
            "city",
            "country_code",
        ]
    ].head(10)
)
print()


# -----------------------------------------------------------------------------
# Extras (if time permits)
# -----------------------------------------------------------------------------

# E1 - Create customer_golden_for_scd2.csv
customer_golden_for_scd2 = customer_golden[
    [
        "customer_business_key",
        "first_name",
        "last_name",
        "email",
        "phone",
        "city",
        "country_code",
        "marketing_consent",
        "completeness_score",
    ]
].copy()

customer_golden_for_scd2.to_csv(
    OUTPUT_DIR / "customer_golden_for_scd2.csv",
    index=False,
)

print("E1 - customer_golden_for_scd2.csv written")
print()


# E2 - Add review output for records where email is missing but phone exists in both systems
missing_email_with_phone = missing_email_review[
    missing_email_review["phone"].notna()
].copy()

phone_groups = (
    missing_email_with_phone.groupby("phone")
    .agg(
        source_row_count=("source_customer_id", "count"),
        source_system_count=("source_system", "nunique"),
    )
    .reset_index()
)

possible_phone_matches = phone_groups[
    phone_groups["source_system_count"] > 1
].copy()

missing_email_phone_review = missing_email_with_phone.merge(
    possible_phone_matches[["phone", "source_row_count", "source_system_count"]],
    on="phone",
    how="inner",
)

missing_email_phone_review.to_csv(
    OUTPUT_DIR / "customer_missing_email_phone_review.csv",
    index=False,
)

print("E2 - customer_missing_email_phone_review.csv written")
print(missing_email_phone_review)
print()


# E3 - Create field_survivorship_notes.csv
field_survivorship_notes = pd.DataFrame([
    {
        "output_column": "customer_business_key",
        "rule": "Use normalized_email.",
    },
    {
        "output_column": "first_name",
        "rule": "Prefer CRM value when available; otherwise use latest non-null value.",
    },
    {
        "output_column": "last_name",
        "rule": "Prefer CRM value when available; otherwise use latest non-null value.",
    },
    {
        "output_column": "email",
        "rule": "Use normalized_email as the standardized email value.",
    },
    {
        "output_column": "phone",
        "rule": "Prefer CRM value when available; otherwise use latest non-null value.",
    },
    {
        "output_column": "address",
        "rule": "Use latest non-null value by source_updated_at.",
    },
    {
        "output_column": "city",
        "rule": "Use latest non-null value by source_updated_at.",
    },
    {
        "output_column": "country_code",
        "rule": "Use latest non-null value by source_updated_at.",
    },
    {
        "output_column": "marketing_consent",
        "rule": "Use latest non-null value by source_updated_at.",
    },
    {
        "output_column": "completeness_score",
        "rule": "Use maximum completeness_score in the matched group.",
    },
])

field_survivorship_notes.to_csv(
    OUTPUT_DIR / "field_survivorship_notes.csv",
    index=False,
)

print("E3 - field_survivorship_notes.csv written")
print()


# E4 - Add country-code validation review output
valid_country_codes = {"FI", "GB", "IT", "SE", "DK", "NO"}

unknown_country_review = candidates[
    candidates["country_code"].notna()
    & ~candidates["country_code"].isin(valid_country_codes)
].copy()

unknown_country_review.to_csv(
    OUTPUT_DIR / "customer_unknown_country_review.csv",
    index=False,
)

print("E4 - customer_unknown_country_review.csv written")
print(unknown_country_review[
    [
        "source_system",
        "source_customer_id",
        "email",
        "country_code",
    ]
])
print()


# -----------------------------------------------------------------------------
# Advanced extras
# -----------------------------------------------------------------------------

# A1 - Create reusable consolidate_customers(crm, webshop) function
def consolidate_customers(crm_input: pd.DataFrame, webshop_input: pd.DataFrame):
    """
    Reusable version of the customer consolidation logic.

    Returns:
        customer_golden
        customer_conflicts
        customer_match_audit
        missing_email_review
    """
    crm_std_local, webshop_std_local = create_standardized_sources(crm_input, webshop_input)

    candidates_local = pd.concat(
        [crm_std_local, webshop_std_local],
        ignore_index=True,
    )

    candidates_local["normalized_email"] = normalize_email(candidates_local["email"])
    candidates_local["source_priority"] = candidates_local["source_system"].map({"crm": 1, "webshop": 2})
    candidates_local["completeness_score"] = candidates_local[score_columns].notna().sum(axis=1)

    missing_email_review_local = candidates_local[
        candidates_local["normalized_email"].isna()
    ].copy()

    matchable_local = candidates_local[
        candidates_local["normalized_email"].notna()
    ].copy()

    # Use the simpler Task 7 version here as well.
    match_audit_base_local = (
        matchable_local.groupby("normalized_email")
        .agg(
            source_row_count=("source_customer_id", "count"),
            max_completeness_score=("completeness_score", "max"),
            newest_source_updated_at=("source_updated_at", "max"),
        )
        .reset_index()
    )

    source_system_rows_local = (
        matchable_local[["normalized_email", "source_system"]]
        .drop_duplicates()
        .sort_values(["normalized_email", "source_system"])
    )

    source_systems_local = (
        source_system_rows_local.groupby("normalized_email")["source_system"]
        .agg(",".join)
        .reset_index(name="source_systems")
    )

    customer_match_audit_local = match_audit_base_local.merge(
        source_systems_local,
        on="normalized_email",
        how="left",
    )

    customer_match_audit_local = customer_match_audit_local[
        [
            "normalized_email",
            "source_row_count",
            "source_systems",
            "max_completeness_score",
            "newest_source_updated_at",
        ]
    ]

    customer_conflicts_local = create_conflicts(matchable_local, conflict_fields)
    customer_golden_local = create_golden_customers(matchable_local)

    return (
        customer_golden_local,
        customer_conflicts_local,
        customer_match_audit_local,
        missing_email_review_local,
    )


a1_customer_golden, a1_conflicts, a1_match_audit, a1_missing_email = consolidate_customers(crm, webshop)

print("A1 - consolidate_customers function result counts")
print("Golden:", len(a1_customer_golden))
print("Conflicts:", len(a1_conflicts))
print("Match audit:", len(a1_match_audit))
print("Missing email:", len(a1_missing_email))
print()


# A2 - Weak match candidate output using normalized phone for records where email is missing
missing_email_with_phone = missing_email_review[
    missing_email_review["phone"].notna()
].copy()

phone_match_audit = (
    missing_email_with_phone.groupby("phone")
    .agg(
        source_row_count=("source_customer_id", "count"),
        source_system_count=("source_system", "nunique"),
    )
    .reset_index()
)

weak_phone_groups = phone_match_audit[
    phone_match_audit["source_row_count"] > 1
].copy()

weak_match_candidates_by_phone = missing_email_with_phone.merge(
    weak_phone_groups[["phone", "source_row_count", "source_system_count"]],
    on="phone",
    how="inner",
)

weak_match_candidates_by_phone["match_type"] = "weak_phone_match_review_only"

weak_match_candidates_by_phone.to_csv(
    OUTPUT_DIR / "customer_weak_match_candidates_by_phone.csv",
    index=False,
)

print("A2 - customer_weak_match_candidates_by_phone.csv written")
print(weak_match_candidates_by_phone)
print()


# A3 - Write customer_golden.csv also as Parquet
# Requires pyarrow or another Parquet engine.
try:
    parquet_file = OUTPUT_DIR / "customer_golden.parquet"
    customer_golden.to_parquet(parquet_file, index=False)
    print("A3 - Wrote:", parquet_file)
except ImportError:
    print("A3 - Parquet write skipped. Install pyarrow if you want to write Parquet:")
    print("     python -m pip install pyarrow")

print()


# A4 - Design how golden customer output could be loaded into customer_golden_stage
a4_design_text = """
Design for loading customer_golden.csv into customer_golden_stage for Lab 7.4B.

Input file:
    output/lab_7_4a/customer_golden_for_scd2.csv

Target table:
    studentXX.customer_golden_stage

Columns:
    customer_business_key varchar(255)
    first_name varchar(100)
    last_name varchar(100)
    email varchar(255)
    phone varchar(50)
    city varchar(100)
    country_code char(2)
    marketing_consent bit
    completeness_score int

Load pattern:
    1. Read customer_golden_for_scd2.csv.
    2. Replace or truncate customer_golden_stage.
    3. Insert the current golden customer rows.
    4. Run the SQL SCD2 procedure from Lab 7.4B.
"""

design_file = OUTPUT_DIR / "customer_golden_stage_load_design.txt"
design_file.write_text(a4_design_text.strip() + "\n", encoding="utf-8")

print("A4 - Design written to:", design_file)


print()
print("Customer consolidation full answer complete.")
print("Output folder:", OUTPUT_DIR)
