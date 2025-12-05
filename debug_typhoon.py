import os
from dotenv import load_dotenv
from typhoon_ocr import ocr_document
import shutil

load_dotenv()

# Ensure API key is set
if os.environ.get("TYPHOON_API_KEY"):
    os.environ["TYPHOON_OCR_API_KEY"] = os.environ.get("TYPHOON_API_KEY")
else:
    print("WARNING: TYPHOON_API_KEY not found in environment variables.")

# Path to a problematic file
original_pdf_path = r"C:\Users\takon\OneDrive\Desktop\da\hack-the-assetdeclaration-data\test phase 1\test phase 1 input\Test_pdf\pdf\จุติ_ไกรฤกษ์_สมาชิกสภาผู้แทนราษฎร_(ส.ส.)_กรณีเข้ารับตำแหน่ง_15_ต.ค._2562.pdf"
safe_pdf_path = "temp_debug.pdf"

def test_ocr(path, description):
    print(f"\n--- Testing {description} ---")
    print(f"File path: {path}")
    if not os.path.exists(path):
        print("File not found!")
        return

    try:
        print("Calling ocr_document...")
        result = ocr_document(pdf_or_image_path=path)
        print("Success!")
        print(f"Result length: {len(result)}")
        print("First 100 chars:", result[:100])
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

# 1. Test with original Thai filename
# test_ocr(original_pdf_path, "Original Thai Filename")

# 2. Test with safe ASCII filename
print("\nCopying to safe filename...")
try:
    shutil.copy(original_pdf_path, safe_pdf_path)
    test_ocr(safe_pdf_path, "Safe ASCII Filename")
except Exception as e:
    print(f"Error copying file: {e}")

# Clean up
if os.path.exists(safe_pdf_path):
    os.remove(safe_pdf_path)
