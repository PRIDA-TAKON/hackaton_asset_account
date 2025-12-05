import os
import time
import json
from src.extractor import extract_data_from_pdf
from src.transformer import transform_json_to_csv

import pandas as pd

# Configuration
INPUT_PDF_DIR = r"C:\Users\takon\OneDrive\Desktop\da\11_hackaton_บัญชีทรัพย์สิน\data\test final\test final input\Test final_pdf"
INPUT_CSV_PATH = r"C:\Users\takon\OneDrive\Desktop\da\11_hackaton_บัญชีทรัพย์สิน\data\test final\test final input\Test final_doc_info.csv"
OUTPUT_DIR = "submission_output"

def load_id_mapping(csv_path):
    try:
        df = pd.read_csv(csv_path)
        mapping = {}
        # Assuming columns: doc_id, doc_location_url, type_id, nacc_id
        # And doc_location_url contains the filename or path
        for _, row in df.iterrows():
            # Extract filename from url/path if needed, or use as is
            # The previous mapping used filename as key.
            # Let's assume doc_location_url is the filename or ends with it.
            filename = os.path.basename(str(row.get('doc_location_url', '')))
            if filename:
                mapping[filename] = {
                    "doc_id": row.get('doc_id'),
                    "nacc_id": row.get('nacc_id')
                }
        print(f"Loaded ID mapping for {len(mapping)} files from {csv_path}")
        return mapping
    except Exception as e:
        print(f"Error loading ID mapping: {e}")
        return {}

def process_all_pdfs():
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    # Get list of PDF files
    if not os.path.exists(INPUT_PDF_DIR):
        print(f"Error: Input directory not found: {INPUT_PDF_DIR}")
        return

    pdf_files = [os.path.join(INPUT_PDF_DIR, f) for f in os.listdir(INPUT_PDF_DIR) if f.lower().endswith('.pdf')]
    total_files = len(pdf_files)
    
    print(f"Found {total_files} PDF files in {INPUT_PDF_DIR}")
    
    # Load ID Mapping dynamically
    ID_MAPPING = load_id_mapping(INPUT_CSV_PATH)

    # Initialize IDs
    current_submitter_id = 50001

    success_count = 0
    fail_count = 0
    
    token_usage_records = []

    for index, pdf_path in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_path)
        print(f"\n[{index}/{total_files}] Processing: {filename}")
        
        # Look up IDs
        if filename in ID_MAPPING:
            mapping = ID_MAPPING[filename]
            current_nacc_id = mapping["nacc_id"]
            # doc_id is available in mapping["doc_id"] if needed, but transformer uses nacc_id as doc_id currently.
            # We should probably update transformer to accept doc_id separately if they differ, 
            # but for now nacc_id is the primary key for summary.
        else:
            print(f"   Warning: No ID mapping found for {filename}. Using fallback ID.")
            current_nacc_id = 90000 + index

        try:
            # 1. Extract
            start_time = time.time()
            data, metadata = extract_data_from_pdf(pdf_path)
            
            if not data:
                print("   Failed to extract data. Generating empty record.")
                # Create empty data structure to ensure a row is generated
                data = {
                    "document_info": {},
                    "submitter": {},
                    "submitter_old_names": [],
                    "submitter_positions": [],
                    "spouse": {},
                    "spouse_old_names": [],
                    "spouse_positions": [],
                    "children": [],
                    "relatives": [],
                    "assets": [],
                    "debts": [],
                    "total_assets": 0.0,
                    "total_debts": 0.0
                }
                fail_count += 1
                
                # Record failure in token usage report
                token_usage_records.append({
                    "ID": filename,
                    "Page Count": 0,
                    "Prompt Tokens": 0,
                    "Output Tokens": 0,
                    "Status": "Failed"
                })
            else:
                success_count += 1
                # Record success in token usage report
                token_usage_records.append({
                    "ID": filename,
                    "Page Count": metadata.get("total_pages", 0) if metadata else 0,
                    "Prompt Tokens": metadata.get("prompt_tokens", 0) if metadata else 0,
                    "Output Tokens": metadata.get("output_tokens", 0) if metadata else 0,
                    "Status": "Success"
                })

            # 2. Transform and Save
            transform_json_to_csv(data, current_nacc_id, current_submitter_id, OUTPUT_DIR)
            
            elapsed = time.time() - start_time
            if data.get("assets"):
                 print(f"   Success! (Time: {elapsed:.2f}s)")
                 print(f"   Assets: {len(data.get('assets', []))}, Debts: {len(data.get('debts', []))}")
            
            # Increment submitter_id only
            current_submitter_id += 1
                
        except Exception as e:
            print(f"   Error processing file: {e}")
            fail_count += 1
            token_usage_records.append({
                "ID": filename,
                "Page Count": 0,
                "Prompt Tokens": 0,
                "Output Tokens": 0,
                "Status": f"Error: {str(e)}"
            })

    # Save Token Usage Report
    report_path = os.path.join(OUTPUT_DIR, "token_usage_report.csv")
    pd.DataFrame(token_usage_records).to_csv(report_path, index=False)
    print(f"\nSaved token usage report to: {report_path}")

    print(f"\n{'='*30}")
    print("Processing Complete")
    print(f"Total Files: {total_files}")
    print(f"Successful: {success_count}")
    print(f"Failed:     {fail_count}")
    print(f"Output Directory: {os.path.abspath(OUTPUT_DIR)}")
    print(f"{'='*30}")

if __name__ == "__main__":
    process_all_pdfs()
