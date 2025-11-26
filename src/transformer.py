import pandas as pd
import os
import csv
from typing import Dict, Any, List

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

    # --- 2. Details CSVs (Train output structure) ---
    process_assets(json_data, nacc_id, submitter_id, details_dir)
    process_spouse(json_data, nacc_id, submitter_id, details_dir)

def process_summary(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
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
        "submitter_sub_district": submitter.get("address", {}).get("sub_district"),
        "submitter_district": submitter.get("address", {}).get("district"),
        "submitter_province": submitter.get("address", {}).get("province"),
        "submitter_post_code": submitter.get("address", {}).get("post_code"),
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
        "statement_detail_count": None,
        "has_statement_detail_note": None,
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
        "relative_count": None,
        "relative_has_death_flag": None
    }
    save_to_csv([summary_row], os.path.join(output_dir, "summary.csv"))

def process_assets(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    assets = json_data.get("assets", [])
    if not assets:
        return

    asset_rows = []
    for idx, asset in enumerate(assets, 1):
        owner = asset.get("owner", "ผู้ยื่น")
        is_submitter = "ผู้ยื่น" in owner
        is_spouse = "คู่สมรส" in owner
        is_child = "บุตร" in owner
        
        # Match Train_asset.csv columns
        row = {
            "asset_id": None, # Generated ID?
            "submitter_id": submitter_id,
            "nacc_id": nacc_id,
            "index": idx,
            "asset_type_id": None, # Need mapping if possible
            "asset_type_other": asset.get("type"),
            "asset_name": asset.get("description"),
            "date_acquiring_type_id": None,
            "acquiring_date": None,
            "acquiring_month": None,
            "acquiring_year": None,
            "date_ending_type_id": None,
            "ending_date": None,
            "ending_month": None,
            "ending_year": None,
            "asset_acquisition_type_id": None,
            "valuation": asset.get("value"),
            "owner_by_submitter": is_submitter,
            "owner_by_spouse": is_spouse,
            "owner_by_child": is_child,
            "latest_submitted_date": json_data.get("document_info", {}).get("submitted_date")
        }
        asset_rows.append(row)
    
    save_to_csv(asset_rows, os.path.join(output_dir, "asset.csv"))

def process_spouse(json_data: Dict[str, Any], nacc_id: int, submitter_id: int, output_dir: str):
    spouse = json_data.get("spouse")
    if not spouse or not spouse.get("first_name"):
        return

    # Match Train_spouse_info.csv columns
    row = {
        "spouse_id": None,
        "submitter_id": submitter_id,
        "nacc_id": nacc_id,
        "title": spouse.get("title"),
        "first_name": spouse.get("first_name"),
        "last_name": spouse.get("last_name"),
        "title_en": None,
        "first_name_en": None,
        "last_name_en": None,
        "age": spouse.get("age"),
        "status": spouse.get("status"),
        "status_date": spouse.get("status_date"), # Need parsing if not YYYY-MM-DD
        "status_month": None,
        "status_year": None,
        "sub_district": None,
        "district": None,
        "province": None,
        "post_code": None,
        "phone_number": None,
        "mobile_number": None,
        "email": None,
        "latest_submitted_date": json_data.get("document_info", {}).get("submitted_date")
    }
    save_to_csv([row], os.path.join(output_dir, "spouse_info.csv"))

def save_to_csv(rows: List[Dict[str, Any]], filepath: str):
    if not rows:
        return
    
    file_exists = os.path.exists(filepath)
    keys = rows[0].keys()
    
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)
