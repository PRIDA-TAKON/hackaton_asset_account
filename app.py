import streamlit as st
import os
import tempfile
import pandas as pd
import shutil
from src.extractor import extract_data_from_pdf
from src.transformer import transform_json_to_csv
from src.drive_loader import download_from_drive
import zipfile

import time

# Page Config
st.set_page_config(
    page_title="Hackathon ข้อมูลบัญชีทรัพย์สิน",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Sporty/Teen Theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton>button {
        background: linear-gradient(45deg, #ff00cc, #3333ff);
        color: white;
        border: none;
        border-radius: 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(255, 0, 204, 0.5);
    }
    h1 {
        font-family: 'Segoe UI', sans-serif;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #ff00cc, #3333ff);
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Hackathon ข้อมูลบัญชีทรัพย์สิน")
st.markdown("### แปลงเอกสารบัญชีทรัพย์สินเป็น Digital Data ด้วย AI สุดล้ำ")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password", value=os.environ.get("api_gemini", ""))
    if api_key:
        os.environ["api_gemini"] = api_key
    
    st.info("Upload PDF or provide Google Drive link to start.")

# Main Area
tab1, tab2 = st.tabs(["📂 File Upload", "☁️ Google Drive"])

processed_data = []
output_dir = "output_csv"

with tab1:
    uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)
    if uploaded_files and st.button("Start Processing Files"):
        if not os.environ.get("api_gemini"):
            st.error("Please provide Gemini API Key!")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            os.makedirs(output_dir, exist_ok=True)
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Extract
                data = extract_data_from_pdf(tmp_path)
                os.remove(tmp_path)
                
                if data:
                    # Transform
                    # Dummy IDs for now if not mapping from doc_info
                    nacc_id = 9999 + i 
                    submitter_id = 8888 + i
                    transform_json_to_csv(data, nacc_id, submitter_id, output_dir)
                    processed_data.append(data)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                time.sleep(4) # Rate limit: 15 RPM = 1 req/4s
            
            status_text.text("Processing Complete! 🎉")
            st.success(f"Processed {len(uploaded_files)} files successfully.")

with tab2:
    drive_link = st.text_input("Google Drive Folder Link")
    if drive_link and st.button("Download & Process from Drive"):
        if not os.environ.get("api_gemini"):
            st.error("Please provide Gemini API Key!")
        else:
            with st.spinner("Downloading files from Drive..."):
                download_dir = "drive_downloads"
                success = download_from_drive(drive_link, download_dir)
                
            if success:
                st.success("Download complete. Starting processing...")
                # Process files in download_dir
                pdf_files = [f for f in os.listdir(download_dir) if f.lower().endswith('.pdf')]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                os.makedirs(output_dir, exist_ok=True)
                
                for i, filename in enumerate(pdf_files):
                    status_text.text(f"Processing {filename}...")
                    pdf_path = os.path.join(download_dir, filename)
                    
                    data = extract_data_from_pdf(pdf_path)
                    
                    if data:
                        nacc_id = 7777 + i
                        submitter_id = 6666 + i
                        transform_json_to_csv(data, nacc_id, submitter_id, output_dir)
                        processed_data.append(data)
                    
                    progress_bar.progress((i + 1) / len(pdf_files))
                    time.sleep(4) # Rate limit: 15 RPM = 1 req/4s
                
                status_text.text("Processing Complete! 🎉")
                st.success(f"Processed {len(pdf_files)} files.")
                
                # Cleanup
                shutil.rmtree(download_dir)
            else:
                st.error("Failed to download from Drive.")

# Download Section
if os.path.exists(output_dir) and os.listdir(output_dir):
    st.divider()
    st.header("📥 Download Results")
    
    # Create Zip
    shutil.make_archive("result_csv", 'zip', output_dir)
    
    with open("result_csv.zip", "rb") as fp:
        btn = st.download_button(
            label="Download All CSVs (ZIP)",
            data=fp,
            file_name="asset_declaration_csv.zip",
            mime="application/zip"
        )
    
    # Preview
    st.subheader("Preview Data")
    
    csv_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".csv"):
                # Store relative path for display
                rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                csv_files.append(rel_path)
                
    if csv_files:
        selected_csv = st.selectbox("Select CSV to preview", csv_files)
        # Construct full path
        full_path = os.path.join(output_dir, selected_csv)
        df = pd.read_csv(full_path)
        st.dataframe(df)
