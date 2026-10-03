"""
Kaggle PlantVillage Dataset Downloader for AgriVision Agent.
Automates downloading, extracting, and organizing crop disease leaf images from Kaggle.
"""

import os
import sys
import argparse
import zipfile
import shutil
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CACHE_DIR = BASE_DIR / "data" / "cache"

DEFAULT_DATASET = "emmarex/plantdisease"


def check_kaggle_auth() -> bool:
    """Checks if Kaggle authentication credentials exist."""
    user_home = Path.home()
    kaggle_dir = user_home / ".kaggle"
    json_path = kaggle_dir / "kaggle.json"
    cred_path = kaggle_dir / "credentials.json"
    token_path = kaggle_dir / "access_token"
    
    has_file = json_path.exists() or cred_path.exists() or token_path.exists()
    has_env = (
        ("KAGGLE_USERNAME" in os.environ and "KAGGLE_KEY" in os.environ)
        or "KAGGLE_API_TOKEN" in os.environ
    )
    return has_file or has_env


def download_from_kaggle(dataset_name: str = DEFAULT_DATASET) -> Path:
    """Downloads dataset from Kaggle using kaggle API."""
    import kaggle

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[*] Authenticating with Kaggle API...")
    kaggle.api.authenticate()
    
    print(f"[*] Downloading '{dataset_name}' from Kaggle to {CACHE_DIR}...")
    kaggle.api.dataset_download_files(dataset_name, path=str(CACHE_DIR), unzip=False, quiet=False)
    
    # Locate downloaded zip file
    zip_files = list(CACHE_DIR.glob("*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No zip archive found in {CACHE_DIR} after Kaggle download.")
    
    latest_zip = max(zip_files, key=os.path.getctime)
    size_mb = latest_zip.stat().st_size / (1024 * 1024)
    print(f"[+] Download complete: {latest_zip.name} ({size_mb:.1f} MB)")
    return latest_zip


def extract_and_organize_dataset(zip_path: Path, target_dir: Path = RAW_DATA_DIR) -> int:
    """
    Extracts the downloaded zip file and organizes leaf class directories into data/raw/.
    Handles various Kaggle folder structures (nested folders, PlantVillage subdirs, etc.).
    """
    extract_temp = CACHE_DIR / "extracted_temp"
    if extract_temp.exists():
        shutil.rmtree(extract_temp)
    extract_temp.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[*] Extracting archive: {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_temp)
    print("[+] Archive extracted successfully.")
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all class folders (folders containing .jpg / .png images)
    print("[*] Scanning and organizing class categories...")
    image_extensions = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
    
    found_classes = {}
    for root, dirs, files in os.walk(extract_temp):
        image_files = [f for f in files if Path(f).suffix in image_extensions]
        if len(image_files) >= 5:  # Valid class folder
            folder_name = Path(root).name
            # Avoid generic directory names
            ignore_names = {"train", "valid", "test", "plantvillage", "segmented", "color", "raw", "images", "extracted_temp"}
            if folder_name.lower() not in ignore_names:
                if folder_name not in found_classes:
                    found_classes[folder_name] = []
                found_classes[folder_name].extend([Path(root) / f for f in image_files])
                
    if not found_classes:
        # Fallback: check one level deeper or direct subfolders
        for item in extract_temp.iterdir():
            if item.is_dir():
                for sub in item.iterdir():
                    if sub.is_dir():
                        imgs = [f for f in sub.glob("*") if f.suffix in image_extensions]
                        if imgs:
                            found_classes[sub.name] = imgs
                            
    print(f"\n[+] Discovered {len(found_classes)} crop disease classes in dataset:")
    total_images_copied = 0
    
    for class_name, img_paths in found_classes.items():
        clean_name = class_name.replace(" ", "_")
        dest_class_dir = target_dir / clean_name
        dest_class_dir.mkdir(parents=True, exist_ok=True)
        
        count = 0
        for p in img_paths:
            dest_file = dest_class_dir / p.name
            if not dest_file.exists():
                shutil.copy2(p, dest_file)
            count += 1
            
        total_images_copied += count
        print(f"  - {clean_name}: {count} leaf images")
        
    # Clean up extraction temp
    try:
        shutil.rmtree(extract_temp)
    except Exception:
        pass
        
    print(f"\n[+] Organization complete! Total images organized in {target_dir}: {total_images_copied}")
    return total_images_copied


def main():
    parser = argparse.ArgumentParser(description="AgriVision Kaggle Dataset Downloader")
    parser.add_argument("--dataset", type=str, default=DEFAULT_DATASET, help="Kaggle dataset handle (e.g. emmarex/plantdisease)")
    parser.add_argument("--zip-file", type=str, default=None, help="Path to already downloaded local zip file")
    args = parser.parse_args()
    
    print("=" * 70)
    print("AgriVision Agent - Kaggle Real Dataset Acquisition Tool")
    print("=" * 70)
    
    if args.zip_file:
        zip_path = Path(args.zip_file)
        if not zip_path.exists():
            print(f"[!] File not found: {zip_path}")
            sys.exit(1)
        extract_and_organize_dataset(zip_path)
        return
        
    if not check_kaggle_auth():
        print("\n[!] Kaggle credentials not found!")
        print("Please run: .venv\\Scripts\\kaggle.exe auth login")
        sys.exit(1)
        
    zip_path = download_from_kaggle(args.dataset)
    extract_and_organize_dataset(zip_path)
    print("\n[+] Dataset is ready in data/raw/ for GPU training!")


if __name__ == "__main__":
    main()

