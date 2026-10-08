"""
Export Haryana Block Agronomy Dataset to mobile asset bundle (scripts/export_mobile_haryana_data.py).
"""
import json
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from src.data.haryana_block_agronomy import HARYANA_BLOCK_AGRONOMY

def export():
    base_dir = Path(__file__).resolve().parent.parent
    target_path = base_dir / "mobile" / "agrivision_app" / "assets" / "haryana_offline_blocks.json"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(HARYANA_BLOCK_AGRONOMY, f, indent=2, ensure_ascii=False)
        
    print(f"Exported {len(HARYANA_BLOCK_AGRONOMY)} Haryana blocks to {target_path} ({target_path.stat().st_size} bytes)")

if __name__ == "__main__":
    export()
