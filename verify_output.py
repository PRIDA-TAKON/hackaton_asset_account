import os
import glob

def verify_output():
    output_dir = "quick_test_output/details"
    summary_dir = "quick_test_output/summary"
    
    expected_files = [
        "Train_submitter_old_name.csv",
        "Train_submitter_position.csv",
        "Train_spouse_info.csv",
        "Train_spouse_old_name.csv",
        "Train_spouse_position.csv",
        "Train_relative_info.csv",
        "Train_statement.csv",
        "Train_statement_detail.csv",
        "Train_asset.csv",
        "Train_asset_building_info.csv",
        "Train_asset_land_info.csv",
        "Train_asset_vehicle_info.csv",
        "Train_asset_other_asset_info.csv"
    ]
    
    print("--- Verifying Output Files ---")
    
    # Check Summary
    if os.path.exists(os.path.join(summary_dir, "Train_summary.csv")):
        print("[PASS] Train_summary.csv found.")
    else:
        print("[FAIL] Train_summary.csv NOT found.")
        
    # Check Details
    all_passed = True
    for filename in expected_files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            print(f"[PASS] {filename} found.")
        else:
            print(f"[FAIL] {filename} NOT found.")
            all_passed = False
            
    if all_passed:
        print("\nAll required files generated successfully!")
    else:
        print("\nSome files are missing.")

if __name__ == "__main__":
    verify_output()
