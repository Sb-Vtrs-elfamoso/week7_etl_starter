from pathlib import Path
import pandas as pd

PROJECT = Path.cwd()
INPUT_DIR = PROJECT / "data" / "customer_sources"
OUTPUT_DIR = PROJECT / "output" / "lab_7_4a"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Project:", PROJECT)
print("Input folder exists:", INPUT_DIR.exists())

# Warm-up 2 - Create a small customer example DataFrame
mini = pd.DataFrame({
    "source_system": ["crm", "webshop", "crm", "webshop"],
    "source_customer_id": ["C001", "W1001", "C002", "W1002"],
    "email": [" Anna@example.com ", "anna@example.com", "matti@example.com", "matti@example.com"],
    "phone": ["+358401111111", None, None, "+358402222222"],
    "city": ["Helsinki", "Helsinki", "Tampere", "Tampere"],
    "marketing_consent": [pd.NA, True, pd.NA, False],
    "source_updated_at": pd.to_datetime(["2024-05-10", "2024-05-20", "2024-05-08", "2024-05-18"]),
})

print(mini)

# Warm-up 3 - Normalize email
mini["normalized_email"] = mini["email"].astype("string").str.strip().str.lower().replace("", pd.NA)
print(mini[["email", "normalized_email"]])

# Warm-up 4 - Count non-null values for completeness
score_columns = ["email", "phone", "city", "marketing_consent", "source_updated_at"]
mini["completeness_score"] = mini[score_columns].notna().sum(axis=1)
print(mini[["source_customer_id", "normalized_email", "completeness_score"]])

# Warm-up 5 - Sort possible duplicates by survivorship priority
mini["source_priority"] = mini["source_system"].map({"crm": 1, "webshop": 2})
ordered = mini.sort_values(
    ["normalized_email", "completeness_score", "source_priority", "source_updated_at"],
    ascending=[True, False, True, False],
)

print(ordered[["source_customer_id", "normalized_email", "completeness_score",
"source_priority", "source_updated_at"]])

# Warm-up 6 - Select one survivor per normalized email
survivors = ordered.drop_duplicates(subset=["normalized_email"], keep="first")
print(survivors[["source_customer_id", "normalized_email", "phone", "city", "completeness_score"]])

# Warm-up 7 - Detect conflicting field values
print("Phone number conflict")
conflict_rows = []

for email, group in mini.groupby("normalized_email"):
    values = sorted({str(v) for v in group["phone"].dropna().unique()})
    if len(values) > 1:
        conflict_rows.append({"normalized_email": email, "field_name": "phone", "values_found": " | ".join(values)})

conflicts = pd.DataFrame(conflict_rows)
print(conflicts)

# Warm-up 8 - Combine two source-shaped DataFrames
crm_small = mini[mini["source_system"].eq("crm")].copy()
web_small = mini[mini["source_system"].eq("webshop")].copy()
combined = pd.concat([crm_small, web_small], ignore_index=True)
print("Combined rows:", len(combined))

# Warm-up 9 - Write a preview output
preview_file = OUTPUT_DIR / "warmup_customer_preview.csv"
survivors.to_csv(preview_file, index=False)
print("Wrote:", preview_file)

# Warm-up 10 - Define helper functions
def normalize_email(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.lower().replace("", pd.NA)

# Required base tasks
# Task 1
# Load both source files and inspect their row counts and column structures.
crm = pd.read_csv(INPUT_DIR / 'crm_customers.csv')
webshop = pd.read_csv(INPUT_DIR / 'webshop_customers.csv')

table_names = ['crm', 'webshop']
tables = [crm, webshop]
for name, table in zip(table_names, tables) :
    print('----- Table', name, '-----')
    print('row count :', len(table))
    print('columns :', table.columns)

# Task 2
# Standardize the CRM extract into the shared customer schema used for matching.
# Helper functions
def normalize_name(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.title().replace("", pd.NA)

def normalize_phone(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.replace(" ", "", regex=False).str.strip()
    s = "+" + s.str.lstrip("+")
    return s.replace("", pd.NA)

def normalize_country_code(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.upper().replace("", pd.NA)

country_code_map = {
    'Finland' : 'FI',
    'UK' : 'GB',
    'Italy' : 'IT',
    'Sweden' : 'SE',
    'Denmark' : 'DK',
    'Norway' : 'NO',
    'Spain' : 'ES'
}
valid_country_codes = set(country_code_map.values())

crm_std = pd.DataFrame()
crm_std['source_customer_id'] = crm['crm_customer_id'].copy()
crm_std['first_name'] = normalize_name(crm['first_name'])
crm_std['last_name'] = normalize_name(crm['last_name'])
crm_std['normalized_email'] = normalize_email(crm['email'])
crm_std['phone'] = normalize_phone(crm['phone'])
crm_std['address'] = crm['street_address'].copy()
crm_std['city'] = crm['city'].copy()
crm_std['country_code'] = normalize_country_code(crm['country'].map(country_code_map))
crm_std['source_updated_at'] = pd.to_datetime(crm['updated_at'])
crm_std['marketing_consent'] = pd.NA
crm_std['source_system'] = 'crm'
print(crm_std)
crm_std.to_csv(OUTPUT_DIR / 'crm_std.csv')

# Task 3
# Standardize the webshop extract and review any invalid country codes from either source.
webshop_std = pd.DataFrame()
webshop_std['source_customer_id'] = webshop['webshop_customer_id'].copy()
webshop_std['first_name'] = normalize_name(webshop['full_name']).str.split(n=1).str[0]
webshop_std['last_name'] = normalize_name(webshop['full_name']).str.split(n=1).str[1]
webshop_std['normalized_email'] = normalize_email(webshop['email'])
webshop_std['phone'] = normalize_phone(webshop['mobile_phone'])
webshop_std['address'] = webshop['address'].copy()
webshop_std['city'] = webshop['city'].copy()
webshop_std['country_code'] = normalize_country_code(webshop['country_code'])
webshop_std['source_updated_at'] = pd.to_datetime(webshop['updated_at'])
webshop_std['marketing_consent'] = normalize_name(webshop['marketing_consent']) == 'True'
webshop_std['source_system'] = 'webshop'
print(webshop_std)
webshop_std.to_csv(OUTPUT_DIR / 'webshop_std.csv')

crm_unknown_country_review = crm_std[
    crm['country'].notna() &
    crm['country'].astype("string").str.strip().ne("") &
    crm_std['country_code'].isna()
].copy()
crm_unknown_country_review['raw_country_value'] = crm.loc[crm_unknown_country_review.index, 'country'].values

webshop_unknown_country_review = webshop_std[
    webshop_std['country_code'].notna() &
    ~webshop_std['country_code'].isin(valid_country_codes)
].copy()
webshop_unknown_country_review['raw_country_value'] = webshop.loc[webshop_unknown_country_review.index, 'country_code'].values

unknown_country_code_review = pd.concat(
    [crm_unknown_country_review, webshop_unknown_country_review],
    ignore_index=True,
)
unknown_country_code_review['review_reason'] = 'unknown_country_code'

crm_std.loc[crm_unknown_country_review.index, 'country_code'] = pd.NA
webshop_std.loc[webshop_unknown_country_review.index, 'country_code'] = pd.NA
unknown_country_code_review.to_csv(
    OUTPUT_DIR / 'customer_unknown_country_code_review.csv',
    index=False,
)

# Task 4
# Stack both standardized sources into one candidate table for consolidation.
candidates = pd.concat([crm_std, webshop_std], ignore_index=True)
print("Combined rows:", len(candidates))

# Task 5
# Split out records that cannot be email-matched and create review files for them.
missing_email_review = candidates[candidates['normalized_email'].isna()]
print(missing_email_review)
missing_email_review.to_csv(OUTPUT_DIR / 'customer_missing_email_review.csv', index=False)

phones_in_both_systems = candidates[candidates['phone'].notna()].groupby('phone')[
    'source_system'
].nunique()
phones_in_both_systems = phones_in_both_systems[phones_in_both_systems.eq(2)].index

missing_email_phone_both_systems_review = candidates[
    candidates['normalized_email'].isna() &
    candidates['phone'].notna() &
    candidates['phone'].isin(phones_in_both_systems)
].copy()
print(missing_email_phone_both_systems_review)
missing_email_phone_both_systems_review.to_csv(
    OUTPUT_DIR / 'customer_missing_email_phone_both_systems_review.csv',
    index=False,
)

valid_candidates = candidates[~candidates['normalized_email'].isna()].copy()

# Task 6
# Score each valid candidate by completeness and add source priority for survivorship.
score_columns = ["first_name", "last_name", "normalized_email", "phone", "address", "city", "country_code", "marketing_consent", "source_updated_at"]
valid_candidates['completeness_score'] = valid_candidates[score_columns].notna().sum(axis=1)
valid_candidates["source_priority"] = valid_candidates["source_system"].map({"crm": 1, "webshop": 2})

print(valid_candidates)

# Task 7
# Build a match audit showing how many source rows contributed to each customer group.
customer_match_audit = valid_candidates.groupby('normalized_email').agg(
    source_row_count=('normalized_email', 'size'),
    source_systems=('source_system', lambda s: sorted(s.unique())),
    max_completeness_score=('completeness_score', 'max'),
    newest_source_updated_at=('source_updated_at', 'max'),
).reset_index()

print(customer_match_audit)
customer_match_audit.to_csv(OUTPUT_DIR / 'customer_match_audit.csv', index=False)

# Task 8
# Detect conflicting values across duplicate customer groups for key business fields.
print("--------- Conflict ---------")
customer_conflicts = []

for email, group in valid_candidates.groupby("normalized_email"):
    # Phone
    values = sorted({str(v) for v in group["phone"].dropna().unique()})
    if len(values) > 1:
        customer_conflicts.append({"normalized_email": email, "field_name": "phone", "values_found": " | ".join(values)})
    # Address
    values = sorted({str(v) for v in group["address"].dropna().unique()})
    if len(values) > 1:
        customer_conflicts.append({"normalized_email": email, "field_name": "address", "values_found": " | ".join(values)})
    # City
    values = sorted({str(v) for v in group["city"].dropna().unique()})
    if len(values) > 1:
        customer_conflicts.append({"normalized_email": email, "field_name": "city", "values_found": " | ".join(values)})
    # Country_code
    values = sorted({str(v) for v in group["country_code"].dropna().unique()})
    if len(values) > 1:
        customer_conflicts.append({"normalized_email": email, "field_name": "country_code", "values_found": " | ".join(values)})
    # Marketing_consent
    values = sorted({str(v) for v in group["marketing_consent"].dropna().unique()})
    if len(values) > 1:
        customer_conflicts.append({"normalized_email": email, "field_name": "marketing_consent", "values_found": " | ".join(values)})

conflicts = pd.DataFrame(customer_conflicts)
print(conflicts)
conflicts.to_csv(OUTPUT_DIR / 'customer_conflicts.csv', index=False)

# Task 9
# Create the golden customer table using survivorship rules for row-level and field-level selection.
ordered_candidates_crm_priority = valid_candidates.sort_values(
    ["normalized_email", "completeness_score", "source_priority", "source_updated_at"],
    ascending=[True, False, True, False],
)
ordered_candidates_update_priority = valid_candidates.sort_values(
    ["normalized_email", "source_updated_at", "completeness_score"],
    ascending=[True, True, True],
)
def last_non_null(series: pd.Series):
    non_null = series.dropna()
    return non_null.iloc[-1] if not non_null.empty else pd.NA

customer_golden = ordered_candidates_crm_priority.drop_duplicates(
    subset=["normalized_email"],
    keep="first",
)[
    ["normalized_email", "source_system", "first_name", "last_name", "phone"]
].reset_index(drop=True)

latest_non_null_fields = ordered_candidates_update_priority.groupby(
    "normalized_email",
    as_index=False,
).agg({
    "address": last_non_null,
    "city": last_non_null,
    "country_code": last_non_null,
    "marketing_consent": last_non_null,
})

customer_golden = customer_golden.merge(
    latest_non_null_fields,
    on="normalized_email",
    how="left",
)
print(customer_golden)
customer_golden.to_csv(OUTPUT_DIR / 'customer_golden.csv', index=False)

# Prepare a slimmed-down golden customer file for the later SCD2 dimension-loading lab.
customer_golden_for_scd2 = customer_golden.rename(
    columns={'normalized_email': 'customer_business_key'}
).copy()
customer_golden_for_scd2['email'] = customer_golden_for_scd2['customer_business_key']
customer_golden_for_scd2['completeness_score'] = customer_golden_for_scd2[
    ['first_name', 'last_name', 'email', 'phone', 'city', 'country_code', 'marketing_consent']
].notna().sum(axis=1)
customer_golden_for_scd2 = customer_golden_for_scd2[
    [
        'customer_business_key',
        'first_name',
        'last_name',
        'email',
        'phone',
        'city',
        'country_code',
        'marketing_consent',
        'completeness_score',
    ]
]
print(customer_golden_for_scd2)
customer_golden_for_scd2.to_csv(
    OUTPUT_DIR / 'customer_golden_for_scd2.csv',
    index=False,
)

# Document which survivorship rule produced each column in the golden record.
field_survivorship_notes = pd.DataFrame([
    {
        'golden_column': 'normalized_email',
        'survivorship_rule': 'group key',
        'rule_detail': 'Use normalized email as the customer match key and golden business identifier.',
    },
    {
        'golden_column': 'source_system',
        'survivorship_rule': 'crm-priority survivor row',
        'rule_detail': 'Take the source system from the top-ranked survivor row sorted by completeness_score desc, source_priority asc, source_updated_at desc.',
    },
    {
        'golden_column': 'first_name',
        'survivorship_rule': 'crm-priority survivor row',
        'rule_detail': 'Take first_name from the top-ranked survivor row sorted by completeness_score desc, source_priority asc, source_updated_at desc.',
    },
    {
        'golden_column': 'last_name',
        'survivorship_rule': 'crm-priority survivor row',
        'rule_detail': 'Take last_name from the top-ranked survivor row sorted by completeness_score desc, source_priority asc, source_updated_at desc.',
    },
    {
        'golden_column': 'phone',
        'survivorship_rule': 'crm-priority survivor row',
        'rule_detail': 'Take phone from the top-ranked survivor row sorted by completeness_score desc, source_priority asc, source_updated_at desc.',
    },
    {
        'golden_column': 'address',
        'survivorship_rule': 'last non-null by update order',
        'rule_detail': 'Within each normalized_email group, sort by source_updated_at asc and completeness_score asc, then keep the last non-null address.',
    },
    {
        'golden_column': 'city',
        'survivorship_rule': 'last non-null by update order',
        'rule_detail': 'Within each normalized_email group, sort by source_updated_at asc and completeness_score asc, then keep the last non-null city.',
    },
    {
        'golden_column': 'country_code',
        'survivorship_rule': 'validated last non-null by update order',
        'rule_detail': 'Unknown country codes are sent to review and nulled out first; then keep the last non-null valid country_code per normalized_email group.',
    },
    {
        'golden_column': 'marketing_consent',
        'survivorship_rule': 'last non-null by update order',
        'rule_detail': 'Within each normalized_email group, sort by source_updated_at asc and completeness_score asc, then keep the last non-null marketing_consent.',
    },
])
print(field_survivorship_notes)
field_survivorship_notes.to_csv(
    OUTPUT_DIR / 'field_survivorship_notes.csv',
    index=False,
)

# Summarize the main row counts and review counts from the customer consolidation run.
customer_consolidation_summary = pd.DataFrame([{
    'candidate_row_count': len(candidates),
    'missing_email_row_count': len(missing_email_review),
    'missing_email_phone_both_systems_review_row_count': len(missing_email_phone_both_systems_review),
    'unknown_country_code_review_row_count': len(unknown_country_code_review),
    'valid_candidate_row_count': len(valid_candidates),
    'matched_customer_count': len(customer_match_audit),
    'customers_in_both_crm_and_webshop_count': customer_match_audit['source_systems'].apply(
        lambda systems: 'crm' in systems and 'webshop' in systems
    ).sum(),
    'conflict_row_count': len(conflicts),
    'golden_customer_row_count': len(customer_golden),
}])
print(customer_consolidation_summary)
customer_consolidation_summary.to_csv(
    OUTPUT_DIR / 'customer_consolidation_summary.csv',
    index=False,
)
