import os
import sys
from dotenv import load_dotenv
from pdf2image import convert_from_path, pdfinfo_from_path

load_dotenv()

print("Checking environment setup...")

# 1. Check API Key
api_key = os.environ.get("api_gemini")
if api_key:
    print(f"✅ API Key found: {api_key[:5]}...")
else:
    print("❌ API Key 'api_gemini' NOT found in environment or .env")

# 2. Check Poppler
try:
    # Try to get info from a dummy or just check if poppler is in path
    # We can't easily check without a PDF, but we can check if pdfinfo is callable
    from pdf2image.exceptions import PDFInfoNotInstalledError
    try:
        # This function internally calls pdfinfo
        # We need a dummy pdf or just rely on the import check if it checks path on init (it doesn't)
        # Let's try to run a subprocess to call pdfinfo
        import subprocess
        subprocess.run(["pdfinfo", "-v"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Poppler (pdfinfo) is installed and in PATH.")
    except FileNotFoundError:
        print("❌ Poppler is NOT found in PATH.")
        print("   Please install Poppler and add it to your PATH.")
        print("   Download: https://github.com/oschwartz10612/poppler-windows/releases/")
    except Exception as e:
        print(f"⚠️ Error checking Poppler: {e}")

except ImportError:
    print("❌ pdf2image library not installed.")

print("Check complete.")
