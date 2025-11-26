import os
import pandas as pd
import glob
import shutil
from src.extractor import extract_data_from_pdf
from src.transformer import transform_json_to_csv
import time

def run_benchmark(limit=3):
    """
    Runs benchmark on a subset of training data.
    """
    base_dir = r"C:\Users\takon\OneDrive\Desktop\da\hack-the-assetdeclaration-data\training"
    pdf_dir = os.path.join(base_dir, "train input", "Train_pdf", "pdf") # Assuming 'pdf' subfolder exists based on previous logs
    if not os.path.exists(pdf_dir):
        pdf_dir = os.path.join(base_dir, "train input", "Train_pdf") # Fallback

    doc_info_path = os.path.join(base_dir, "train input", "Train_doc_info.csv")
    gt_summary_path = os.path.join(base_dir, "train summary", "Train_summary.csv")
    gt_asset_path = os.path.join(base_dir, "train output", "Train_asset.csv")
    
    output_dir = "benchmark_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Load Ground Truth
    print("Loading Ground Truth...")
    doc_info = pd.read_csv(doc_info_path)
    gt_summary = pd.read_csv(gt_summary_path)
    gt_assets = pd.read_csv(gt_asset_path)
    
    # Select subset
    subset = doc_info.head(limit)
    
    results = []
    
    print(f"Starting benchmark on {len(subset)} files...")
    
    for index, row in subset.iterrows():
        filename = row['doc_location_url']
        nacc_id = row['nacc_id']
        pdf_path = os.path.join(pdf_dir, filename)
        
        print(f"\nProcessing [{index+1}/{len(subset)}]: {filename} (NACC ID: {nacc_id})")
        
        if not os.path.exists(pdf_path):
            print(f"  Error: File not found at {pdf_path}")
            continue
            
        # Extract
        try:
            start_time = time.time()
            data = extract_data_from_pdf(pdf_path)
            duration = time.time() - start_time
            
            if not data:
                print("  Error: Extraction returned None")
                results.append({
                    "filename": filename,
                    "status": "Failed",
                    "duration": duration
                })
                continue
                
            # Transform
            # Create a specific output folder for this file to avoid overwriting if we were running parallel (though we aren't)
            # But transformer appends, so we should clear or use unique folders. 
            # Transformer creates 'summary' and 'details' inside the given dir.
            # Let's use a temp dir for this file.
            file_output_dir = os.path.join(output_dir, str(nacc_id))
            os.makedirs(file_output_dir, exist_ok=True)
            
            transform_json_to_csv(data, nacc_id, 9999, file_output_dir)
            
            # Load Predictions
            pred_summary_path = os.path.join(file_output_dir, "summary", "summary.csv")
            pred_asset_path = os.path.join(file_output_dir, "details", "asset.csv")
            
            # Compare Summary (Total Valuation)
            gt_summ_row = gt_summary[gt_summary['nacc_id'] == nacc_id]
            gt_total_val = gt_summ_row.iloc[0]['asset_total_valuation_amount'] if not gt_summ_row.empty else 0
            
            if os.path.exists(pred_summary_path):
                pred_summ_df = pd.read_csv(pred_summary_path)
                pred_total_val = pred_summ_df.iloc[0]['asset_total_valuation_amount'] if not pred_summ_df.empty else 0
            else:
                pred_total_val = 0
                
            # Compare Asset Count
            gt_asset_rows = gt_assets[gt_assets['nacc_id'] == nacc_id]
            gt_asset_count = len(gt_asset_rows)
            
            if os.path.exists(pred_asset_path):
                pred_asset_df = pd.read_csv(pred_asset_path)
                pred_asset_count = len(pred_asset_df)
            else:
                pred_asset_count = 0
            
            # Calculate Accuracy (Simple % match)
            val_diff = abs(gt_total_val - pred_total_val)
            val_match_pct = max(0, 100 - (val_diff / (gt_total_val + 1) * 100)) # Simple diff pct
            
            count_diff = abs(gt_asset_count - pred_asset_count)
            count_match_pct = max(0, 100 - (count_diff / (gt_asset_count + 1) * 100))
            
            print(f"  GT Assets: {gt_asset_count}, Pred: {pred_asset_count}")
            print(f"  GT Value: {gt_total_val:,.2f}, Pred: {pred_total_val:,.2f}")
            
            results.append({
                "filename": filename,
                "status": "Success",
                "duration": duration,
                "gt_asset_count": gt_asset_count,
                "pred_asset_count": pred_asset_count,
                "gt_total_val": gt_total_val,
                "pred_total_val": pred_total_val,
                "val_match_pct": val_match_pct,
                "count_match_pct": count_match_pct
            })
            
            # Rate limit
            time.sleep(4)
            
        except Exception as e:
            print(f"  Error: {str(e)}")
            results.append({"filename": filename, "status": "Error", "error": str(e)})

    # Summary Report
    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        print(df_results[['filename', 'gt_asset_count', 'pred_asset_count', 'gt_total_val', 'pred_total_val']])
        
        if 'val_match_pct' in df_results.columns:
            print(f"\nAverage Valuation Match: {df_results['val_match_pct'].mean():.2f}%")
            print(f"Average Asset Count Match: {df_results['count_match_pct'].mean():.2f}%")
    else:
        print("No results generated.")

if __name__ == "__main__":
    run_benchmark(limit=3) # Run on 3 files by default
