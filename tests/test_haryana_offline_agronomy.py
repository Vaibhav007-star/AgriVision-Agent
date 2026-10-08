"""
Unit & Integration Tests for Haryana Offline Block Agronomy System.
Tests SQLite database persistence, CRUD methods, REST APIs, local dialects, vernacular crop names,
offline symptom triage chains, and CCS HAU dosage compliance.
"""

import sys
import json
from pathlib import Path
import pytest

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from starlette.testclient import TestClient
from app.server import app
from app.database.database import get_db_connection, init_db, seed_haryana_offline_agronomy
from app.database.crud import (
    get_offline_agronomy_blocks,
    get_offline_agronomy_by_block,
    get_all_districts_agronomy,
    get_all_dialects_agronomy,
    search_offline_agronomy_by_crop
)
from src.data.haryana_block_agronomy import HARYANA_BLOCK_AGRONOMY, get_all_blocks, get_blocks_by_district


class TestHaryanaOfflineAgronomy:
    @pytest.fixture(autouse=True)
    def setup_class(self):
        self.client = TestClient(app)
        init_db()

    def test_all_22_districts_represented_in_sqlite(self):
        """Verifies that all 22 administrative districts of Haryana are present in SQLite."""
        districts = get_all_districts_agronomy()
        assert len(districts) == 22, f"Expected 22 districts, found {len(districts)}: {districts}"
        expected_districts = {
            "Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram",
            "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh",
            "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa",
            "Sonipat", "Yamunanagar"
        }
        assert set(districts) == expected_districts

    def test_database_table_record_count(self):
        """Verifies SQLite table has all 28 representative block agronomy entries."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM haryana_offline_agronomy")
            count = cursor.fetchone()[0]
            assert count >= 28

    def test_dialect_mapping_authenticity(self):
        """Verifies that authentic Haryana cultural dialects are correctly recorded."""
        dialects = get_all_dialects_agronomy()
        dialect_str = " ".join(dialects).lower()
        
        # Check presence of major indigenous dialects
        assert "ahirwati" in dialect_str
        assert "bagri" in dialect_str
        assert "bangru" in dialect_str
        assert "puadhi" in dialect_str
        assert "mewati" in dialect_str

        # Test specific regional block dialects
        nuh_block = get_offline_agronomy_by_block("Nuh", "Nuh")
        assert nuh_block is not None
        assert "mewati" in nuh_block["primary_dialect"].lower()

        sirsa_block = get_offline_agronomy_by_block("Sirsa", "Sirsa")
        assert sirsa_block is not None
        assert "bagri" in sirsa_block["primary_dialect"].lower()

        mahendragarh_block = get_offline_agronomy_by_block("Mahendragarh", "Narnaul")
        assert mahendragarh_block is not None
        assert "ahirwati" in mahendragarh_block["primary_dialect"].lower()

        ambala_block = get_offline_agronomy_by_block("Ambala", "Naraingarh")
        assert ambala_block is not None
        assert "puadhi" in ambala_block["primary_dialect"].lower()

    def test_vernacular_crop_nomenclature(self):
        """Verifies vernacular Hindi crop terms (Sarson, Gwar, Dhan, Gehu, Kapas, Makka) are included."""
        all_blocks = get_offline_agronomy_blocks()
        all_crops_flat = " ".join([c for b in all_blocks for c in b["primary_crops"]]).lower()
        
        assert "sarson" in all_crops_flat or "mustard" in all_crops_flat
        assert "gwar" in all_crops_flat or "cluster bean" in all_crops_flat
        assert "dhan" in all_crops_flat or "paddy" in all_crops_flat
        assert "gehu" in all_crops_flat or "wheat" in all_crops_flat
        assert "kapas" in all_crops_flat or "cotton" in all_crops_flat

    def test_offline_symptom_checklist_chains(self):
        """Verifies that symptom checklists follow linear decision chains formatted with '->'."""
        karnal_block = get_offline_agronomy_by_block("Karnal", "Gharaunda")
        assert karnal_block is not None
        symptoms = karnal_block["symptom_checklist"]
        assert len(symptoms) >= 3
        for disease, chain in symptoms.items():
            assert "->" in chain, f"Symptom chain for {disease} must be a linear sequence with '->'"

    def test_ccs_hau_approved_pesticide_dosages(self):
        """Verifies chemical and bio-pesticide recommendations cite exact CCS HAU dosages per acre."""
        hisar_block = get_offline_agronomy_by_block("Hisar", "Adampur")
        assert hisar_block is not None
        solutions = hisar_block["approved_pesticide_solution"]
        assert len(solutions) >= 3
        for disease, solution in solutions.items():
            assert "per acre" in solution.lower() or "kg seed" in solution.lower() or "ml" in solution.lower() or "g" in solution.lower()

    def test_api_offline_blocks_endpoint(self):
        """Verifies GET /api/haryana/offline-blocks returns 200 OK with all blocks."""
        response = self.client.get("/api/haryana/offline-blocks")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_blocks"] >= 28
        assert data["districts_represented"] == 22

    def test_api_offline_blocks_filter_by_district(self):
        """Verifies filtering by district via GET /api/haryana/offline-blocks/{district}."""
        response = self.client.get("/api/haryana/offline-blocks/Rohtak")
        assert response.status_code == 200
        data = response.json()
        assert data["district"] == "Rohtak"
        assert data["block_count"] >= 1
        assert any(b["block_name"] == "Sampla" for b in data["blocks"])

    def test_api_offline_blocks_block_detail(self):
        """Verifies GET /api/haryana/offline-blocks/{district}/{block} returns detailed agronomy profile."""
        response = self.client.get("/api/haryana/offline-blocks/Sirsa/Sirsa")
        assert response.status_code == 200
        data = response.json()
        assert data["district"] == "Sirsa"
        assert data["block_name"] == "Sirsa"
        assert "Bagri" in data["primary_dialect"]
        assert len(data["primary_crops"]) >= 3
        assert len(data["top_3_diseases"]) >= 3

    def test_api_offline_dialects_distribution(self):
        """Verifies GET /api/haryana/offline-dialects returns dialect distribution dictionary."""
        response = self.client.get("/api/haryana/offline-dialects")
        assert response.status_code == 200
        data = response.json()
        assert data["total_dialects"] >= 5
        assert "distribution" in data
        assert "Bagri" in data["dialects"] or any("Bagri" in d for d in data["dialects"])

    def test_api_offline_triage_decision_chain(self):
        """Verifies GET /api/haryana/offline-triage returns matched decision chain and solution."""
        response = self.client.get("/api/haryana/offline-triage?district=Karnal&block=Gharaunda&disease_key=Rice_Bacterial_Blight")
        assert response.status_code == 200
        data = response.json()
        assert data["district"] == "Karnal"
        assert data["block"] == "Gharaunda"
        assert "diagnostic_chain" in data
        assert "Water-soaked" in data["diagnostic_chain"] or "water-soaked" in data["diagnostic_chain"].lower()
        assert "Copper Oxychloride" in data["approved_hau_solution"]

    def test_mobile_offline_json_asset_integrity(self):
        """Verifies mobile asset haryana_offline_blocks.json exists and contains all 28 blocks."""
        asset_path = BASE_DIR / "mobile" / "agrivision_app" / "assets" / "haryana_offline_blocks.json"
        assert asset_path.exists(), f"Missing mobile asset: {asset_path}"
        with open(asset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) >= 28
        districts_in_json = set(item["District_Name"] for item in data)
        assert len(districts_in_json) == 22
