import os
import json
import google.generativeai as genai
from pdf2image import convert_from_path
from typing import Optional, Dict, Any
import base64
import io
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ.get("api_gemini"))

def extract_data_from_pdf(pdf_path: str, api_key: str = None) -> Optional[Dict[str, Any]]:
    """
    Extracts asset declaration data from a PDF file using Gemini API.
    """
    if api_key:
        genai.configure(api_key=api_key)
    elif not os.environ.get("api_gemini"):
        # Try to load from env if not passed and not already set
        # (Though module level load_dotenv should have handled it, this is a safety check)
        pass

    try:
        # 1. Convert PDF to Images
        print(f"Processing {pdf_path}...")
        images = convert_from_path(pdf_path)
        
        # Prepare images for Gemini
        image_parts = []
        for img in images:
            # Resize if too large to save tokens/bandwidth (optional but good practice)
            # img.thumbnail((1024, 1024)) 
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            image_parts.append({
                "mime_type": "image/jpeg",
                "data": img_byte_arr.getvalue()
            })

        # 2. Construct Prompt
        # We import the schema to ensure the model follows it, 
        # but for the prompt we can just describe it or pass the schema as text.
        # Using response_schema is better if available, but for simplicity/compatibility
        # we will use a strong system instruction with JSON mode.
        
        system_instruction = """
        You are an expert data extraction AI. Your task is to extract structured data from Thai Asset Declaration documents (บัญชีทรัพย์สินและหนี้สิน).
        
        Please extract the following information and return it as a VALID JSON object matching this structure:
        {
            "document_info": {
                "submitted_date": "YYYY-MM-DD",
                "disclosure_date": "YYYY-MM-DD"
            },
            "submitter": {
                "title": "...",
                "first_name": "...",
                "last_name": "...",
                "age": 0,
                "position": "...",
                "agency": "...",
                "marital_status": "โสด/สมรส/หย่า/...",
                "address": {
                    "sub_district": "...",
                    "district": "...",
                    "province": "...",
                    "post_code": "..."
                }
            },
            "spouse": {
                "title": "...",
                "first_name": "...",
                "last_name": "...",
                "age": 0,
                "status": "จดทะเบียนสมรส/...",
                "status_date": "YYYY-MM-DD"
            },
            "children": [
                { "title": "...", "first_name": "...", "last_name": "...", "age": 0 }
            ],
            "assets": [
                {
                    "description": "...",
                    "value": 1000.00,
                    "type": "เงินสด/เงินฝาก/ที่ดิน/โรงเรือน/ยานพาหนะ/สิทธิ/อื่น ๆ",
                    "owner": "ผู้ยื่น/คู่สมรส/บุตร"
                }
            ],
            "debts": [
                {
                    "description": "...",
                    "value": 1000.00,
                    "owner": "ผู้ยื่น/คู่สมรส/บุตร"
                }
            ],
            "total_assets": 0.00,
            "total_debts": 0.00
        }

        Rules:
        1. Extract ALL assets and debts listed.
        2. Use "ผู้ยื่น", "คู่สมรส", "บุตร" for owner field.
        4. If a field is missing, use null.
        5. Dates should be in YYYY-MM-DD format (Convert Thai year to AD: subtract 543).
        6. For asset types, map them to standard categories if possible: เงินสด, เงินฝาก, เงินลงทุน, ที่ดิน, โรงเรือนและสิ่งปลูกสร้าง, ยานพาหนะ, สิทธิและสัมปทาน, ทรัพย์สินอื่น.
        """

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite", # User requested specific model
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.1,
            },
            system_instruction=system_instruction
        )

        # 3. Call API
        # 
        prompt_parts = ["Extract data from these asset declaration pages."] + image_parts
        
        response = model.generate_content(prompt_parts)
        
        # 4. Parse Response
        json_text = response.text
        data = json.loads(json_text)
        return data

    except Exception as e:
        print(f"Error extracting data from {pdf_path}: {e}")
        return None

if __name__ == "__main__":
    # Test with a dummy path if run directly
    pass
