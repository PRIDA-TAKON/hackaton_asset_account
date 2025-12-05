import os
import json
import google.generativeai as genai
from pdf2image import convert_from_path
from typing import Optional, Dict, Any
import base64
import io
from PIL import Image
from dotenv import load_dotenv
from typhoon_ocr import ocr_document

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

from src.schema import AssetDeclaration

def extract_data_from_pdf(pdf_path: str, api_key: str = None) -> (Optional[Dict[str, Any]], Optional[Dict[str, int]]):
    """
    Extracts asset declaration data from a PDF file using Gemini API.
    Uses pagination to handle large documents and avoid output token limits.
    """
    if api_key:
        genai.configure(api_key=api_key)
    elif not os.environ.get("api_gemini"):
        pass

    try:
        # 1. Convert PDF to Images (Bypass Typhoon's internal PDF handling which fails on Windows/Thai)
        print(f"Processing {pdf_path}...")
        try:
            images = convert_from_path(pdf_path)
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return None, None
            
        total_pages = len(images)
        print(f"Total pages: {total_pages}")
        
        # Ensure API key is set for typhoon-ocr
        if os.environ.get("TYPHOON_API_KEY"):
            os.environ["TYPHOON_OCR_API_KEY"] = os.environ.get("TYPHOON_API_KEY")

        # Chunking configuration
        CHUNK_SIZE = 2
        all_data = {
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
        
        total_prompt_tokens = 0
        total_output_tokens = 0
        last_gemini_call_time = 0
        
        # Process in chunks of pages
        for i in range(0, total_pages, CHUNK_SIZE):
            chunk_images = images[i : i + CHUNK_SIZE]
            print(f"  Processing chunk {i//CHUNK_SIZE + 1} (Pages {i+1}-{min(i+CHUNK_SIZE, total_pages)})...")
            
            chunk_markdown_text = ""
            
            # OCR each page in the chunk
            for j, img in enumerate(chunk_images):
                page_num = i + j + 1
                print(f"    OCR Page {page_num}...")
                
                temp_img_path = f"temp_page_{page_num}.jpg"
                img.save(temp_img_path, "JPEG")
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Typhoon Rate Limit: 20 RPM -> 1 request every 3 seconds
                        print(f"    Sleeping for 3 seconds (Typhoon Limit)... Attempt {attempt+1}/{max_retries}")
                        import time
                        time.sleep(3)
                        
                        page_text = ocr_document(pdf_or_image_path=temp_img_path)
                        chunk_markdown_text += f"\n\n--- Page {page_num} ---\n\n" + page_text
                        print(f"    Page {page_num} OCR Complete. Length: {len(page_text)}")
                        break # Success, exit retry loop
                        
                    except Exception as e:
                        print(f"    Error OCRing page {page_num} (Attempt {attempt+1}): {e}")
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 5 # Linear backoff: 5s, 10s
                            print(f"    Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                        else:
                            print(f"    Failed to OCR page {page_num} after {max_retries} attempts.")
                            pass
                
                # Cleanup temp file
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
            
            # Structure chunk data with Gemini
            if chunk_markdown_text:
                # Gemini Rate Limit: 10 RPM -> 1 request every 6 seconds
                import time
                elapsed = time.time() - last_gemini_call_time
                if elapsed < 6:
                    wait_time = 6 - elapsed
                    print(f"    Sleeping for {wait_time:.2f} seconds (Gemini Limit)...")
                    time.sleep(wait_time)
                
                print(f"    Structuring chunk {i//CHUNK_SIZE + 1} with Gemini...")
                chunk_data, usage = structure_data_with_gemini(chunk_markdown_text)
                last_gemini_call_time = time.time()
                
                if usage:
                    total_prompt_tokens += usage.get("prompt_tokens", 0)
                    total_output_tokens += usage.get("output_tokens", 0)
                
                if chunk_data:
                    # Merge logic
                    if not all_data["submitter"] and chunk_data.get("submitter"):
                        all_data["submitter"] = chunk_data["submitter"]
                    if not all_data["document_info"] and chunk_data.get("document_info"):
                        all_data["document_info"] = chunk_data["document_info"]
                    if not all_data["spouse"] and chunk_data.get("spouse"):
                        all_data["spouse"] = chunk_data["spouse"]
                    
                    all_data["submitter_old_names"].extend(chunk_data.get("submitter_old_names") or [])
                    all_data["submitter_positions"].extend(chunk_data.get("submitter_positions") or [])
                    all_data["spouse_old_names"].extend(chunk_data.get("spouse_old_names") or [])
                    all_data["spouse_positions"].extend(chunk_data.get("spouse_positions") or [])
                    all_data["children"].extend(chunk_data.get("children") or [])
                    all_data["relatives"].extend(chunk_data.get("relatives") or [])
                    all_data["assets"].extend(chunk_data.get("assets") or [])
                    all_data["debts"].extend(chunk_data.get("debts") or [])
                else:
                    print(f"    Warning: Failed to extract data from chunk {i//CHUNK_SIZE + 1}")

        print(f"   Token Usage: Prompt: {total_prompt_tokens}, Output: {total_output_tokens}, Total: {total_prompt_tokens + total_output_tokens}")
        
        metadata = {
            "total_pages": total_pages,
            "prompt_tokens": total_prompt_tokens,
            "output_tokens": total_output_tokens
        }
        return all_data, metadata

    except Exception as e:
        print(f"Error extracting data from {pdf_path}: {e}")
        return None, None

def structure_data_with_gemini(text: str) -> (Optional[Dict[str, Any]], Optional[Dict[str, int]]):
    try:
        system_instruction = """
        You are an expert data extraction AI specialized in Thai Government Asset Declaration documents (บัญชีทรัพย์สินและหนี้สิน).
        
        Your Goal: Extract structured data from the provided OCR text of the document.
        
        CRITICAL RULES:
        1. **Extract EVERYTHING**: Do not summarize. Extract every single row from every table.
        2. **Asset & Debt Details**:
           - Extract the full description, value, and owner for EACH item.
           - If a value is "-", "ไม่มี", or blank, treat it as 0.0 unless specified otherwise.
           - "ผู้ยื่น" = Submitter, "คู่สมรส" = Spouse, "บุตร" = Children.
        3. **Submitter Info**: Usually found on the first few pages. Extract Name, Position, Agency, and Address.
        4. **Strict JSON**: Output ONLY valid JSON matching the schema.
        """

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": AssetDeclaration,
                "temperature": 0.1,
                "max_output_tokens": 16384,
            },
            system_instruction=system_instruction
        )

        prompt_parts = [f"Extract data from this asset declaration text:\n\n{text}"]
        
        response = model.generate_content(prompt_parts)
        
        usage = {
            "prompt_tokens": response.usage_metadata.prompt_token_count,
            "output_tokens": response.usage_metadata.candidates_token_count
        }
        
        json_text = response.text
        
        # Clean up markdown code blocks if present
        if json_text.strip().startswith("```json"):
            json_text = json_text.strip().split("\n", 1)[1]
            if json_text.strip().endswith("```"):
                json_text = json_text.strip().rsplit("\n", 1)[0]
        elif json_text.strip().startswith("```"):
             json_text = json_text.strip().split("\n", 1)[1]
             if json_text.strip().endswith("```"):
                json_text = json_text.strip().rsplit("\n", 1)[0]

        data = json.loads(json_text)
        sanitized_data = sanitize_data(data)
        return sanitized_data, usage
        
    except Exception as e:
        print(f"    Gemini structuring error: {e}")
        return None, None

def sanitize_data(data: Any) -> Any:
    """Recursively sanitizes data to remove JSON artifacts from strings."""
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, str):
        # Remove newlines and excessive whitespace
        clean_str = " ".join(data.split())
        # Check for suspicious JSON-like characters in fields that shouldn't have them
        # (This is a heuristic; might need adjustment)
        if "{" in clean_str and "}" in clean_str and ":" in clean_str:
             # Likely raw JSON leaked into a string field
             return ""
        return clean_str
    else:
        return data

if __name__ == "__main__":
    # Test with a dummy path if run directly
    pass
