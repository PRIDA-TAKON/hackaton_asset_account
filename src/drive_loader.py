import gdown
import os
import zipfile

def download_from_drive(url: str, output_dir: str):
    """
    Downloads a file or folder from Google Drive.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Check if it's a folder link
        if "drive.google.com/drive/folders" in url:
            print("Downloading folder...")
            # gdown folder download is tricky, often requires --folder flag in CLI
            # or using gdown.download_folder
            gdown.download_folder(url, output=output_dir, quiet=False, use_cookies=False)
        else:
            print("Downloading file...")
            output_path = os.path.join(output_dir, "downloaded_file")
            gdown.download(url, output_path, quiet=False, fuzzy=True)
            
            # If zip, extract
            if zipfile.is_zipfile(output_path):
                with zipfile.ZipFile(output_path, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                os.remove(output_path)
                
        return True
    except Exception as e:
        print(f"Error downloading from Drive: {e}")
        return False
