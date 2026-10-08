"""
Script to append Section 9 on Haryana Offline-First Block Agronomy to AgriVision_Plant_Disease_Detection_Guide.docx
"""
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def update_docx():
    docx_path = Path("AgriVision_Plant_Disease_Detection_Guide.docx")
    if not docx_path.exists():
        print(f"Error: {docx_path} does not exist.")
        return

    doc = Document(str(docx_path))
    
    # Add Section Heading
    h1 = doc.add_heading("9. Haryana Offline-First Block Agronomy, Micro-Dialects & CCS HAU Prescriptions", level=1)
    
    p_intro = doc.add_paragraph(
        "To empower marginal and smallholder farmers across rural Haryana without requiring continuous "
        "cellular connectivity, AgriVision incorporates a dedicated 100% Offline-First Micro-Regional Agronomy Database. "
        "This system directly bridges linguistic and diagnostic barriers right at the farm gate."
    )
    
    # Subsection A
    doc.add_heading("A. Technical Architecture & Edge Delivery", level=2)
    doc.add_paragraph(
        "1. On-Device SQLite Engine (data/agrivision.db):\n"
        "   - Table 'haryana_offline_agronomy' persists 30 representative administrative blocks across all 22 districts.\n"
        "   - Zero network overhead; queries run synchronously in sub-millisecond execution times.\n\n"
        "2. Embedded Mobile JSON Bundle (mobile/agrivision_app/assets/haryana_offline_blocks.json):\n"
        "   - Packaged directly within the offline Flutter APK/AAB bundle.\n"
        "   - Read offline via rootBundle through OfflineAgronomyService with in-memory fast indexing.\n\n"
        "3. FastAPI Edge Services (app/server.py):\n"
        "   - Endpoints /api/haryana/offline-blocks, /api/haryana/offline-blocks/{district}/{block}, and "
        "/api/haryana/offline-triage serve low-latency cached agronomic payloads."
    )
    
    # Subsection B
    doc.add_heading("B. Micro-Regional Linguistic Dialects Mapping", level=2)
    
    dialects_data = [
        ("Regional Zone", "Linguistic Dialect", "Districts & Administrative Blocks Covered"),
        ("North-East Belt", "Puadhi", "Ambala (Naraingarh, Barara), Yamunanagar (Bilaspur, Jagadhri), Panchkula (Raipur Rani), Kurukshetra (Shahabad)"),
        ("Khadar / Yamuna Belt", "Bangru / Khadar Haryanvi", "Karnal (Gharaunda, Assandh), Panipat (Samalkha), Sonipat (Gohana), Kaithal (Guhla)"),
        ("Central Plains", "Deshwali Haryanvi", "Rohtak (Sampla, Meham), Jhajjar (Bahadurgarh, Beri), Jind (Safidon, Narwana)"),
        ("Western Cotton Belt", "Bagri", "Sirsa (Sirsa, Ellenabad, Dabwali), Fatehabad (Tohana), Hisar (Adampur, Hansi), Bhiwani (Siwani, Tosham)"),
        ("Southern Ahirwal Belt", "Ahirwati (Raathi)", "Mahendragarh (Narnaul), Rewari (Bawal, Kosli), Charkhi Dadri (Badhra), Gurugram (Pataudi)"),
        ("Mewat Micro-Region", "Mewati", "Nuh (Nuh, Taoru, Ferozepur Jhirka, Punahana)"),
        ("Braj Fringe", "Braj", "Palwal (Hodal, Hathin), Ballabgarh / Faridabad fringe"),
    ]
    
    table = doc.add_table(rows=len(dialects_data), cols=3)
    table.autofit = False
    
    for row_idx, row in enumerate(dialects_data):
        for col_idx, text in enumerate(row):
            cell = table.cell(row_idx, col_idx)
            cell.text = text
            if row_idx == 0:
                set_cell_background(cell, "2E7D32")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if row_idx % 2 == 1:
                    set_cell_background(cell, "F1F8E9")
                    
    doc.add_paragraph("")
    
    # Subsection C
    doc.add_heading("C. Vernacular Crop Taxonomy & Linear Diagnostic Chains", level=2)
    doc.add_paragraph(
        "Crop profiles utilize authentic local vernacular terms (Dhan, Gehu, Sarson, Gwar, Kapas, Makka, Aloo, Tamatar) "
        "alongside scientific botanical taxonomy to support voice readout and mobile audio accessibility.\n\n"
        "Each block features a linear diagnostic chain (Step 1 -> Step 2 -> Step 3) allowing farmers to visually self-triage diseases offline:\n"
        "• Karnal (Rice Bacterial Blight): Leaf tips turn water-soaked -> Lesions turn yellow-white with wavy margins along veins -> "
        "Bacterial ooze droplets visible in early morning -> Leaves wilt and dry (Kresek symptom).\n"
        "  - CCS HAU Approved Solution: Copper Oxychloride 50% WP @ 500 g + Streptocycline @ 6 g in 200 L water per acre.\n\n"
        "• Sirsa (Cotton Pink Bollworm): Rosetted flowers that fail to open -> Larvae bore into tender bolls -> "
        "Bolls open prematurely with stained lint and damaged seeds.\n"
        "  - CCS HAU Approved Solution: Emamectin Benzoate 5% SG @ 100 g or Spinetoram 11.7% SC @ 170 ml in 200 L water per acre at ETL.\n\n"
        "• Nuh (Mustard Alternaria Blight): Concentric target-board brown circular spots on leaves -> "
        "Black lesions on siliquae (pods) -> Premature pod shattering.\n"
        "  - CCS HAU Approved Solution: Mancozeb 75% WP @ 600-800 g or Iprodione 50% WP @ 400 g in 200 L water per acre."
    )

    doc.save(str(docx_path))
    print(f"Successfully updated {docx_path} with Section 9.")

if __name__ == "__main__":
    update_docx()
