import pandas as pd
import os
import csv
import warnings
from typing import Dict, Any, List, Optional

# Suppress FutureWarning from pandas about downcasting
warnings.simplefilter(action='ignore', category=FutureWarning)

def transform_json_to_csv(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, base_output_dir: str):
    """
    Transforms extracted JSON data into CSV files in the output directory.
    Creates 'summary' and 'details' subfolders.
    """
    summary_dir = os.path.join(base_output_dir, "summary")
    details_dir = os.path.join(base_output_dir, "details")
    
    os.makedirs(summary_dir, exist_ok=True)
    os.makedirs(details_dir, exist_ok=True)
    
    # --- 1. Summary CSV (Train_summary structure) ---
    process_summary(json_data, nacc_id, submitter_id, summary_dir)

    # --- 2. Details CSVs (Test structure - kept for compatibility/completeness) ---
    process_doc_info(json_data, nacc_id, details_dir)
    process_nacc_detail(json_data, nacc_id, submitter_id, details_dir)
    process_submitter_info(json_data, submitter_id, details_dir)
    
    # --- 3. Train Output CSVs (13 files) ---
    # 1. Train_submitter_old_name.csv
    process_submitter_old_name(json_data, nacc_id, submitter_id, details_dir)
    # 2. Train_submitter_position.csv
    process_submitter_position(json_data, nacc_id, submitter_id, details_dir)
    # 3. Train_spouse_info.csv
    process_spouse_info(json_data, nacc_id, submitter_id, details_dir)
    # 4. Train_spouse_old_name.csv
    process_spouse_old_name(json_data, nacc_id, submitter_id, details_dir)
    # 5. Train_spouse_position.csv
    process_spouse_position(json_data, nacc_id, submitter_id, details_dir)
    # 6. Train_relative_info.csv
    process_relative_info(json_data, nacc_id, submitter_id, details_dir)
    # 7. Train_statement.csv
    process_statement(json_data, nacc_id, submitter_id, details_dir)
    # 8. Train_statement_detail.csv
    process_statement_detail(json_data, nacc_id, submitter_id, details_dir)
    # 9. Train_asset.csv
    process_asset(json_data, nacc_id, submitter_id, details_dir)
    # 10. Train_asset_building_info.csv
    process_asset_building(json_data, nacc_id, submitter_id, details_dir)
    # 11. Train_asset_land_info.csv
    process_asset_land(json_data, nacc_id, submitter_id, details_dir)
    # 12. Train_asset_vehicle_info.csv
    process_asset_vehicle(json_data, nacc_id, submitter_id, details_dir)
    # 13. Train_asset_other_asset_info.csv
    process_asset_other(json_data, nacc_id, submitter_id, details_dir)

def process_doc_info(json_data: Dict[str, Any], nacc_id: int, output_dir: str):
    fieldnames = ["doc_id", "doc_location_url", "type_id", "nacc_id"]
    row = {
        "doc_id": nacc_id,
        "doc_location_url": None,
        "type_id": None,
        "nacc_id": nacc_id
    }
    save_to_csv([row], os.path.join(output_dir, "Test_doc_info.csv"), fieldnames)

def process_nacc_detail(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["nacc_id", "title", "first_name", "last_name", "position", "submitted_case", "submitted_date", "disclosure_announcement_date", "disclosure_start_date", "disclosure_end_date", "agency", "date_by_submitted_case", "royal_start_date", "create_at", "submitter_id"]
    submitter = json_data.get("submitter", {})
    doc_info = json_data.get("document_info", {})
    row = {
        "nacc_id": nacc_id,
        "title": submitter.get("title"),
        "first_name": submitter.get("first_name"),
        "last_name": submitter.get("last_name"),
        "position": submitter.get("position"),
        "submitted_case": None,
        "submitted_date": doc_info.get("submitted_date"),
        "disclosure_announcement_date": None,
        "disclosure_start_date": doc_info.get("disclosure_date"),
        "disclosure_end_date": None,
        "agency": submitter.get("agency"),
        "date_by_submitted_case": None,
        "royal_start_date": None,
        "create_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "submitter_id": submitter_id
    }
    save_to_csv([row], os.path.join(output_dir, "Test_nacc_detail.csv"), fieldnames)

def process_submitter_info(json_data: Dict[str, Any], submitter_id: int, output_dir: str):
    fieldnames = ["submitter_id", "title", "first_name", "last_name", "title_en", "first_name_en", "last_name_en", "age", "status", "status_date", "status_month", "status_year", "sub_district", "district", "province", "post_code", "phone_number", "mobile_number", "email", "latest_submitted_date"]
    submitter = json_data.get("submitter", {})
    address = submitter.get("address") or {}
    doc_info = json_data.get("document_info", {})
    row = {
        "submitter_id": submitter_id,
        "title": submitter.get("title"),
        "first_name": submitter.get("first_name"),
        "last_name": submitter.get("last_name"),
        "title_en": None,
        "first_name_en": None,
        "last_name_en": None,
        "age": submitter.get("age"),
        "status": submitter.get("marital_status"),
        "status_date": None,
        "status_month": None,
        "status_year": None,
        "sub_district": address.get("sub_district"),
        "district": address.get("district"),
        "province": address.get("province"),
        "post_code": address.get("post_code"),
        "phone_number": None,
        "mobile_number": None,
        "email": None,
        "latest_submitted_date": doc_info.get("submitted_date")
    }
    save_to_csv([row], os.path.join(output_dir, "Test_submitter_info.csv"), fieldnames)

def process_submitter_old_name(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["submitter_id", "nacc_id", "old_first_name", "old_last_name", "changed_date"]
    old_names = json_data.get("submitter_old_names", [])
    rows = []
    for on in old_names:
        rows.append({
            "submitter_id": submitter_id,
            "nacc_id": nacc_id,
            "old_first_name": on.get("old_first_name"),
            "old_last_name": on.get("old_last_name"),
            "changed_date": on.get("changed_date")
        })
    save_to_csv(rows, os.path.join(output_dir, "Train_submitter_old_name.csv"), fieldnames)

def process_submitter_position(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["submitter_id", "nacc_id", "position", "agency", "start_date", "end_date"]
    positions = json_data.get("submitter_positions", [])
    rows = []
    for pos in positions:
        rows.append({
            "submitter_id": submitter_id,
            "nacc_id": nacc_id,
            "position": pos.get("position"),
            "agency": pos.get("agency"),
            "start_date": pos.get("start_date"),
            "end_date": pos.get("end_date")
        })
    save_to_csv(rows, os.path.join(output_dir, "Train_submitter_position.csv"), fieldnames)

def process_spouse_info(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["spouse_id", "submitter_id", "nacc_id", "title", "first_name", "last_name", "age", "status", "status_date"]
    spouse = json_data.get("spouse", {})
    rows = []
    if spouse and spouse.get("first_name"):
        rows.append({
            "spouse_id": None,
            "submitter_id": submitter_id,
            "nacc_id": nacc_id,
            "title": spouse.get("title"),
            "first_name": spouse.get("first_name"),
            "last_name": spouse.get("last_name"),
            "age": spouse.get("age"),
            "status": spouse.get("status"),
            "status_date": spouse.get("status_date")
        })
    save_to_csv(rows, os.path.join(output_dir, "Train_spouse_info.csv"), fieldnames)

def process_spouse_old_name(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["spouse_id", "nacc_id", "old_first_name", "old_last_name", "changed_date"]
    old_names = json_data.get("spouse_old_names", [])
    rows = []
    for on in old_names:
        rows.append({
            "spouse_id": None,
            "nacc_id": nacc_id,
            "old_first_name": on.get("old_first_name"),
            "old_last_name": on.get("old_last_name"),
            "changed_date": on.get("changed_date")
        })
    save_to_csv(rows, os.path.join(output_dir, "Train_spouse_old_name.csv"), fieldnames)

def process_spouse_position(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["spouse_id", "nacc_id", "position", "agency", "start_date", "end_date"]
    positions = json_data.get("spouse_positions", [])
    rows = []
    for pos in positions:
        rows.append({
            "spouse_id": None,
            "nacc_id": nacc_id,
            "position": pos.get("position"),
            "agency": pos.get("agency"),
            "start_date": pos.get("start_date"),
            "end_date": pos.get("end_date")
        })
    save_to_csv(rows, os.path.join(output_dir, "Train_spouse_position.csv"), fieldnames)

def process_relative_info(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["relative_id", "submitter_id", "nacc_id", "relation", "title", "first_name", "last_name", "age", "is_alive"]
    relatives = json_data.get("relatives", [])
    rows = []
    for rel in relatives:
        rows.append({
            "relative_id": None,
            "submitter_id": submitter_id,
            "nacc_id": nacc_id,
            "relation": rel.get("relation"),
            "title": rel.get("title"),
            "first_name": rel.get("first_name"),
            "last_name": rel.get("last_name"),
            "age": rel.get("age"),
            "is_alive": rel.get("is_alive")
        })
    save_to_csv(rows, os.path.join(output_dir, "Train_relative_info.csv"), fieldnames)

def process_statement(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["nacc_id", "submitter_id", "submitted_date", "disclosure_date"]
    doc_info = json_data.get("document_info", {})
    row = {
        "nacc_id": nacc_id,
        "submitter_id": submitter_id,
        "submitted_date": doc_info.get("submitted_date"),
        "disclosure_date": doc_info.get("disclosure_date")
    }
    save_to_csv([row], os.path.join(output_dir, "Train_statement.csv"), fieldnames)

def process_statement_detail(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    # Placeholder for detailed statement info
    fieldnames = ["nacc_id", "submitter_id", "detail_type", "detail_value"] # Example fields
    rows = []
    save_to_csv(rows, os.path.join(output_dir, "Train_statement_detail.csv"), fieldnames)

def process_asset(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["asset_id", "submitter_id", "nacc_id", "description", "value", "type", "owner"]
    assets = json_data.get("assets", [])
    rows = []
    for idx, asset in enumerate(assets, 1):
        rows.append({
            "asset_id": f"{nacc_id}_{idx}",
            "submitter_id": submitter_id,
            "nacc_id": nacc_id,
            "description": asset.get("description"),
            "value": asset.get("value"),
            "type": asset.get("type"),
            "owner": asset.get("owner")
        })
    save_to_csv(rows, os.path.join(output_dir, "Train_asset.csv"), fieldnames)

def process_asset_building(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["asset_id", "location", "province", "doc_number", "acquisition_date"]
    assets = json_data.get("assets", [])
    rows = []
    for idx, asset in enumerate(assets, 1):
        if "โรงเรือน" in str(asset.get("type", "")):
            rows.append({
                "asset_id": f"{nacc_id}_{idx}",
                "location": asset.get("location"),
                "province": asset.get("province"),
                "doc_number": asset.get("doc_number"),
                "acquisition_date": asset.get("acquisition_date")
            })
    save_to_csv(rows, os.path.join(output_dir, "Train_asset_building_info.csv"), fieldnames)

def process_asset_land(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["asset_id", "location", "province", "doc_number", "acquisition_date"]
    assets = json_data.get("assets", [])
    rows = []
    for idx, asset in enumerate(assets, 1):
        if "ที่ดิน" in str(asset.get("type", "")):
            rows.append({
                "asset_id": f"{nacc_id}_{idx}",
                "location": asset.get("location"),
                "province": asset.get("province"),
                "doc_number": asset.get("doc_number"),
                "acquisition_date": asset.get("acquisition_date")
            })
    save_to_csv(rows, os.path.join(output_dir, "Train_asset_land_info.csv"), fieldnames)

def process_asset_vehicle(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["asset_id", "province", "doc_number", "acquisition_date"]
    assets = json_data.get("assets", [])
    rows = []
    for idx, asset in enumerate(assets, 1):
        if "ยานพาหนะ" in str(asset.get("type", "")):
            rows.append({
                "asset_id": f"{nacc_id}_{idx}",
                "province": asset.get("province"),
                "doc_number": asset.get("doc_number"),
                "acquisition_date": asset.get("acquisition_date")
            })
    save_to_csv(rows, os.path.join(output_dir, "Train_asset_vehicle_info.csv"), fieldnames)

def process_asset_other(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["asset_id", "description", "acquisition_date"]
    assets = json_data.get("assets", [])
    rows = []
    for idx, asset in enumerate(assets, 1):
        atype = str(asset.get("type", ""))
        if "อื่น" in atype or ("ที่ดิน" not in atype and "โรงเรือน" not in atype and "ยานพาหนะ" not in atype):
            rows.append({
                "asset_id": f"{nacc_id}_{idx}",
                "description": asset.get("description"),
                "acquisition_date": asset.get("acquisition_date")
            })
    save_to_csv(rows, os.path.join(output_dir, "Train_asset_other_asset_info.csv"), fieldnames)

def process_summary(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    fieldnames = ["id", "doc_id", "nd_title", "nd_first_name", "nd_last_name", "nd_position", "submitted_date", "disclosure_announcement_date", "disclosure_start_date", "disclosure_end_date", "date_by_submitted_case", "royal_start_date", "agency", "submitter_id", "submitter_title", "submitter_first_name", "submitter_last_name", "submitter_age", "submitter_marital_status", "submitter_status_date", "submitter_status_month", "submitter_status_year", "submitter_sub_district", "submitter_district", "submitter_province", "submitter_post_code", "submitter_phone_number", "submitter_mobile_number", "submitter_email", "spouse_id", "spouse_title", "spouse_first_name", "spouse_last_name", "spouse_age", "spouse_status", "spouse_status_date", "spouse_status_month", "spouse_status_year", "statement_valuation_submitter_total", "statement_valuation_spouse_total", "statement_valuation_child_total", "statement_detail_count", "has_statement_detail_note", "asset_count", "asset_land_count", "asset_building_count", "asset_vehicle_count", "asset_other_count", "asset_total_valuation_amount", "asset_land_valuation_amount", "asset_building_valuation_amount", "asset_vehicle_valuation_amount", "asset_other_asset_valuation_amount", "asset_valuation_submitter_amount", "asset_valuation_spouse_amount", "asset_valuation_child_amount", "relative_count", "relative_has_death_flag"]
    submitter = json_data.get("submitter", {})
    spouse = json_data.get("spouse", {})
    doc_info = json_data.get("document_info", {})
    assets = json_data.get("assets", [])
    
    # Calculate aggregates
    asset_count = len(assets)
    asset_land_count = sum(1 for a in assets if "ที่ดิน" in str(a.get("type", "")))
    asset_building_count = sum(1 for a in assets if "โรงเรือน" in str(a.get("type", "")))
    asset_vehicle_count = sum(1 for a in assets if "ยานพาหนะ" in str(a.get("type", "")))
    asset_other_count = asset_count - (asset_land_count + asset_building_count + asset_vehicle_count)
    
    asset_total_val = sum(float(a.get("value", 0) or 0) for a in assets)
    asset_land_val = sum(float(a.get("value", 0) or 0) for a in assets if "ที่ดิน" in str(a.get("type", "")))
    asset_building_val = sum(float(a.get("value", 0) or 0) for a in assets if "โรงเรือน" in str(a.get("type", "")))
    asset_vehicle_val = sum(float(a.get("value", 0) or 0) for a in assets if "ยานพาหนะ" in str(a.get("type", "")))
    asset_other_val = asset_total_val - (asset_land_val + asset_building_val + asset_vehicle_val)

    asset_submitter_val = sum(float(a.get("value", 0) or 0) for a in assets if "ผู้ยื่น" in str(a.get("owner", "")))
    asset_spouse_val = sum(float(a.get("value", 0) or 0) for a in assets if "คู่สมรส" in str(a.get("owner", "")))
    asset_child_val = sum(float(a.get("value", 0) or 0) for a in assets if "บุตร" in str(a.get("owner", "")))

    relatives = json_data.get("relatives", [])
    relative_count = len(relatives)

    summary_row = {
        "id": nacc_id,
        "doc_id": nacc_id,
        "nd_title": submitter.get("title"),
        "nd_first_name": submitter.get("first_name"),
        "nd_last_name": submitter.get("last_name"),
        "nd_position": submitter.get("position"),
        "submitted_date": doc_info.get("submitted_date"),
        "disclosure_announcement_date": None,
        "disclosure_start_date": doc_info.get("disclosure_date"),
        "disclosure_end_date": None,
        "date_by_submitted_case": None,
        "royal_start_date": None,
        "agency": submitter.get("agency"),
        "submitter_id": submitter_id,
        "submitter_title": submitter.get("title"),
        "submitter_first_name": submitter.get("first_name"),
        "submitter_last_name": submitter.get("last_name"),
        "submitter_age": submitter.get("age"),
        "submitter_marital_status": submitter.get("marital_status"),
        "submitter_status_date": None,
        "submitter_status_month": None,
        "submitter_status_year": None,
        "submitter_sub_district": (submitter.get("address") or {}).get("sub_district"),
        "submitter_district": (submitter.get("address") or {}).get("district"),
        "submitter_province": (submitter.get("address") or {}).get("province"),
        "submitter_post_code": (submitter.get("address") or {}).get("post_code"),
        "submitter_phone_number": None,
        "submitter_mobile_number": None,
        "submitter_email": None,
        "spouse_id": None,
        "spouse_title": spouse.get("title"),
        "spouse_first_name": spouse.get("first_name"),
        "spouse_last_name": spouse.get("last_name"),
        "spouse_age": spouse.get("age"),
        "spouse_status": spouse.get("status"),
        "spouse_status_date": spouse.get("status_date"),
        "spouse_status_month": None,
        "spouse_status_year": None,
        "statement_valuation_submitter_total": asset_submitter_val,
        "statement_valuation_spouse_total": asset_spouse_val,
        "statement_valuation_child_total": asset_child_val,
        "statement_detail_count": 0,
        "has_statement_detail_note": 0,
        "asset_count": asset_count,
        "asset_land_count": asset_land_count,
        "asset_building_count": asset_building_count,
        "asset_vehicle_count": asset_vehicle_count,
        "asset_other_count": asset_other_count,
        "asset_total_valuation_amount": asset_total_val,
        "asset_land_valuation_amount": asset_land_val,
        "asset_building_valuation_amount": asset_building_val,
        "asset_vehicle_valuation_amount": asset_vehicle_val,
        "asset_other_asset_valuation_amount": asset_other_val,
        "asset_valuation_submitter_amount": asset_submitter_val,
        "asset_valuation_spouse_amount": asset_spouse_val,
        "asset_valuation_child_amount": asset_child_val,
        "relative_count": relative_count,
        "relative_has_death_flag": 0
    }
    save_to_csv([summary_row], os.path.join(output_dir, "Train_summary.csv"), fieldnames)

def save_to_csv(rows: List[Dict[str, Any]], filepath: str, fieldnames: Optional[List[str]] = None):
    if not rows:
        if fieldnames and not os.path.exists(filepath):
            pd.DataFrame(columns=fieldnames).to_csv(filepath, index=False)
        return
    
    df = pd.DataFrame(rows)
    
    # Ensure all fieldnames are present
    if fieldnames:
        for col in fieldnames:
            if col not in df.columns:
                df[col] = None
        df = df[fieldnames]
        
    # Fill NaNs with 0
    df = df.fillna(0)
    # Replace empty strings (or whitespace only) with 0
    df = df.replace(r'^\s*$', 0, regex=True)
        
    file_exists = os.path.exists(filepath)
    
    # Append to CSV
    # mode='a' for append, header=not file_exists to write header only if file is new
    df.to_csv(filepath, mode='a', index=False, header=not file_exists)
