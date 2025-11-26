import os
import glob
from src.extractor import extract_data_from_pdf
from src.transformer import transform_json_to_csv
import json

def quick_test():
    # Specific PDF path provided by user
    test_pdf = r"C:\Users\takon\OneDrive\Desktop\da\11_hackaton_บัญชีทรัพย์สิน\hack-the-assetdeclaration-data\test phase 1\test phase 1 input\Test_pdf\pdf\เกื้อกูล_ด่านชัยวิจิตร_สมาชิกสภาผู้แทนราษฎร_(ส.ส.)_กรณีพ้นจากตำแหน่ง_12_มิ.ย._2566.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"File not found: {test_pdf}")
        return

    print(f"Testing with: {os.path.basename(test_pdf)}")
    
    data = extract_data_from_pdf(test_pdf)
    
    if data:
        print("\n--- Extraction Success ---")
        submitter = data.get('submitter', {})
        if submitter:
            print(f"Submitter: {submitter.get('first_name')} {submitter.get('last_name')}")
        
        assets = data.get('assets', [])
        debts = data.get('debts', [])
        print(f"Total Assets: {len(assets)}")
        print(f"Total Debts: {len(debts)}")
        
        # Test transform
        output_dir = "quick_test_output"
        transform_json_to_csv(data, 1234, 5678, output_dir)
        print(f"\nCSV generated in {output_dir}")
    else:
        print("Extraction failed.")

if __name__ == "__main__":
    quick_test()
