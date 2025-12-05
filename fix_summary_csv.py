import pandas as pd
import os

def fix_csv(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Fixing {file_path}...")
    df = pd.read_csv(file_path)

    # List of columns that should be numeric and default to 0
    numeric_cols = [
        "statement_detail_count",
        "has_statement_detail_note",
        "relative_count",
        "relative_has_death_flag",
        "statement_valuation_submitter_total",
        "statement_valuation_spouse_total",
        "statement_valuation_child_total",
        "asset_count",
        "asset_land_count",
        "asset_building_count",
        "asset_vehicle_count",
        "asset_other_count",
        "asset_total_valuation_amount",
        "asset_land_valuation_amount",
        "asset_building_valuation_amount",
        "asset_vehicle_valuation_amount",
        "asset_other_asset_valuation_amount",
        "asset_valuation_submitter_amount",
        "asset_valuation_spouse_amount",
        "asset_valuation_child_amount",
        "submitter_age",
        "spouse_age"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Fill all other NaNs with "0" as requested
    df = df.fillna("0")
    
    # Also replace empty strings with "0"
    df = df.replace(r'^\s*$', '0', regex=True)

    # Clean up rows that contain raw JSON/Markdown leakage
    # We check if 'nd_title' or 'submitter_title' contains suspicious characters like '{', '}', or double quotes that shouldn't be there
    # Or if the row count doesn't match expected columns (though pandas handles this, bad rows might be merged)
    
    def is_valid_row(row):
        # Check for JSON-like content in text fields
        for col in ['nd_title', 'submitter_title', 'nd_first_name']:
            val = str(row[col])
            if '{' in val or '}' in val or '""' in val or 'first_name' in val:
                return False
        return True

    # Filter out bad rows
    initial_count = len(df)
    df = df[df.apply(is_valid_row, axis=1)]
    final_count = len(df)
    
    if initial_count != final_count:
        print(f"Removed {initial_count - final_count} rows containing invalid data (JSON leakage).")

    df.to_csv(file_path, index=False)
    print("Done!")

if __name__ == "__main__":
    fix_csv(r"C:\Users\takon\OneDrive\Desktop\da\11_hackaton_บัญชีทรัพย์สิน\submission_output\summary\Train_summary.csv")
