"""
AgriVision Agent — Vernacular Voice & Dialect Parsing Engine
Handles Haryanvi, Hindi, Hinglish, and English voice queries from farmers,
extracting crop, pathology symptoms, regional district, and providing CCS HAU Hisar
grounded prescriptions with synthesized spoken audio scripts.
"""

from typing import Dict, Any, List, Optional
import re
import unicodedata


# ============================================================================
# Vernacular Agricultural Lexicon & Dialect Mapping
# ============================================================================

CROPS_LEXICON = {
    "Wheat": {
        "keywords": ["कनक", "गेहूं", "गेहूँ", "kanak", "gehu", "gehun", "wheat"],
        "hindi_name": "गेहूं (कनक)",
        "scientific_name": "Triticum aestivum",
        "common_diseases": ["Yellow Rust (पीला रतुआ)", "Loose Smut (कांगुआ रोग)", "Karnal Bunt", "Powdery Mildew"]
    },
    "Paddy / Rice": {
        "keywords": ["धान", "बासमती", "चावल", "झीरी", "dhan", "dhaan", "basmati", "chawal", "rice", "paddy", "jheeri"],
        "hindi_name": "धान (बासमती)",
        "scientific_name": "Oryza sativa",
        "common_diseases": ["Bacterial Leaf Blight (झुलसा)", "Bakanae / Foot Rot (झंडा रोग)", "Sheath Blight", "Blast"]
    },
    "Cotton": {
        "keywords": ["नरमा", "कपास", "रुई", "narma", "kapas", "cotton"],
        "hindi_name": "कपास (नरमा)",
        "scientific_name": "Gossypium hirsutum",
        "common_diseases": ["Pink Bollworm (गुलाबी सूंढी)", "Whitefly (सफेद मक्खी)", "Cotton Leaf Curl Virus", "Bacterial Blight"]
    },
    "Tomato": {
        "keywords": ["टमाटर", "tamatar", "tomato"],
        "hindi_name": "टमाटर",
        "scientific_name": "Solanum lycopersicum",
        "common_diseases": ["Early Blight (अगेती झुलसा)", "Late Blight (पछेती झुलसा)", "Leaf Curl Virus", "Bacterial Wilt"]
    },
    "Potato": {
        "keywords": ["आलू", "aloo", "aalu", "potato"],
        "hindi_name": "आलू",
        "scientific_name": "Solanum tuberosum",
        "common_diseases": ["Early Blight", "Late Blight (पछेती झुलसा)", "Scab", "Black Scurf"]
    },
    "Mustard": {
        "keywords": ["सरसों", "सरसो", "राई", "तोरिया", "sarson", "sarso", "mustard", "toria"],
        "hindi_name": "सरसों / राई",
        "scientific_name": "Brassica juncea",
        "common_diseases": ["White Rust (सफेद रतुआ)", "Downy Mildew", "Alternaria Blight", "Aphids (चेपा)"]
    },
    "Sugarcane": {
        "keywords": ["गन्ना", "गन्ने", "पोंडा", "ganna", "ganne", "sugarcane", "ponda"],
        "hindi_name": "गन्ना",
        "scientific_name": "Saccharum officinarum",
        "common_diseases": ["Red Rot (लाल सड़न)", "Smut", "Wilt", "Top Borer"]
    },
    "Pearl Millet / Bajra": {
        "keywords": ["बाजरा", "बाजरी", "bajra", "bajri", "millet"],
        "hindi_name": "बाजरा",
        "scientific_name": "Pennisetum glaucum",
        "common_diseases": ["Downy Mildew / Green Ear (जोगिया रोग)", "Ergot", "Smut"]
    }
}

SYMPTOM_DISEASE_RULES = [
    {
        "id": "wheat_yellow_rust",
        "crop": "Wheat",
        "triggers": ["पीला", "पीले", "पिलिया", "रतुआ", "धारी", "peela", "yellow", "rust", "stripes", "ratawa"],
        "disease": "Yellow / Stripe Rust (पीला रतुआ - Puccinia striiformis)",
        "severity": "HIGH",
        "symptoms_summary": "पत्तियों की ऊपरी सतह पर समानांतर पीली धारियों में पाउडरनुमा फफोले।",
        "treatment_hi": "200 मिली प्रोपिकोनाजोल 25% EC (टिल्ट) को 200 लीटर पानी में मिलाकर प्रति एकड़ छिड़काव करें। 15 दिन बाद आवश्यकता पड़ने पर दोहराएं।",
        "treatment_haryanvi": "म्हारी कनक म पीला रतुआ का अटैक सै। तुरंत 200 लीटर पाणी म 200 मिली प्रोपिकोनाजोल (टिल्ट) मिलाकै साफ मौसम म छिड़क द्यो।",
        "treatment_en": "Spray Propiconazole 25% EC (Tilt) @ 200 ml in 200 L water per acre at first sign of yellow stripe appearance."
    },
    {
        "id": "wheat_loose_smut",
        "crop": "Wheat",
        "triggers": ["कांगुआ", "काला", "काली बाली", "smut", "loose smut", "black head", "kala"],
        "disease": "Loose Smut (कांगुआ रोग - Ustilago tritici)",
        "severity": "HIGH",
        "symptoms_summary": "बालियों में दानों की जगह काला चूर्ण बन जाना।",
        "treatment_hi": "प्रभावित बालियों को पॉलीथीन थैली से ढककर खेत से बाहर निकालकर नष्ट करें। अगली बुवाई पर बीज को टेबुकोनाजोल 2% DS (1 ग्राम/किग्रा) से उपचारित करें।",
        "treatment_haryanvi": "काली बालियां नै पोलोथिन म ढककै खेत तै बाहर गाड़ द्यो। आगली बार बीजाई पै टैबुकोनाजोल तै बीज शोधन जरूर करियो।",
        "treatment_en": "Rogue out infected black ears in plastic bags and destroy. Treat next season seeds with Tebuconazole 2% DS @ 1.0 g/kg seed."
    },
    {
        "id": "rice_bacterial_blight",
        "crop": "Paddy / Rice",
        "triggers": ["झुलसा", "पत्ते सूख", "सफेद पत्ते", "jhulsa", "blight", "bacterial", "tip dry", "sukha"],
        "disease": "Bacterial Leaf Blight (पत्ती का झुलसा - Xanthomonas oryzae)",
        "severity": "HIGH",
        "symptoms_summary": "पत्तियों के किनारे लहरदार रूप में पीले-सफेद होकर सूखने लगते हैं और सुबह के समय जीवाणु का रिसाव दिखता है।",
        "treatment_hi": "कॉपर ऑक्सीक्लोराइड 50% WP (500 ग्राम) + स्ट्रेप्टोसाइक्लिन (6 ग्राम) को 200 लीटर पानी में मिलाकर प्रति एकड़ छिड़कें। यूरिया का उपयोग तुरंत रोक दें।",
        "treatment_haryanvi": "धान म पत्ती झुलसा का रोग सै। यूरिया घालणा बंद करो अर 500 ग्राम कॉपर + 6 ग्राम स्ट्रेप्टोसाइक्लिन 200 लीटर पाणी म मिलाकै स्प्रे करो।",
        "treatment_en": "Halt nitrogen top-dressing. Spray Copper Oxychloride 50% WP @ 500 g + Streptocycline @ 6 g in 200 L water per acre."
    },
    {
        "id": "rice_bakanae",
        "crop": "Paddy / Rice",
        "triggers": ["झंडा रोग", "लंबा पौधा", "बाकाणे", "bakanae", "jhanda", "foot rot", "tall"],
        "disease": "Bakanae / Foot Rot (झंडा रोग - Fusarium fujikuroi)",
        "severity": "CRITICAL",
        "symptoms_summary": "पौधे अन्य स्वस्थ पौधों से असामान्य रूप से लंबे, पीले और पतले होकर सूख जाते हैं।",
        "treatment_hi": "संक्रमित पौधों को जड़ सहित उखाड़कर नष्ट करें। कार्बेन्डाजिम 50% WP (2 ग्राम/लीटर पानी) की दर से जड़ों के पास ड्रेंचिंग करें।",
        "treatment_haryanvi": "लंबे निकड़े झंडे पौधों नै जड़ तै पाट कै नष्ट करो। कार्बेन्डाजिम 2 ग्राम प्रति लीटर के हिसाब तै ड्रेचिंग करो।",
        "treatment_en": "Pull out and incinerate elongated diseased plants. Drench root zones with Carbendazim 50% WP @ 2.0 g/L water."
    },
    {
        "id": "cotton_pink_bollworm",
        "crop": "Cotton",
        "triggers": ["गुलाबी", "सूंढी", "सुंडी", "कीड़ा", "टिंडा", "pink", "bollworm", "sundi", "sundhi", "keeda"],
        "disease": "Pink Bollworm (गुलाबी सूंढी - Pectinophora gossypiella)",
        "severity": "CRITICAL",
        "symptoms_summary": "गुलाब के फूल जैसा खिलना (Rosetted flower) तथा टिंडों में छेद होकर अंदर बीज व लिंट का नष्ट होना।",
        "treatment_hi": "खेत में फेरोमोन ट्रैप (8 ट्रैप प्रति एकड़) लगाएं। प्रकोप दिखने पर प्रोफेनोफॉस 50% EC @ 500 मिली या स्पाइनोसैड 45% SC @ 75 मिली प्रति 200 लीटर पानी में छिड़कें।",
        "treatment_haryanvi": "नरमा म गुलाबी सूंढी का भारी प्रकोप सै। 8 फेरोमोन ट्रैप लगाओ अर 500 मिली प्रोफेनोफॉस 200 लीटर पाणी म मिलाकै सांझ कै बखत छिड़को।",
        "treatment_en": "Install 8 Pheromone traps/acre. Spray Profenofos 50% EC @ 500 ml or Spinosad 45% SC @ 75 ml in 200 L water per acre during evening hours."
    },
    {
        "id": "tomato_early_blight",
        "crop": "Tomato",
        "triggers": ["अगेती", "धब्बे", "छल्ले", "गोल", "early", "blight", "target", "dhabbe"],
        "disease": "Early Blight (अगेती झुलसा - Alternaria solani)",
        "severity": "MODERATE",
        "symptoms_summary": "निचली पत्तियों पर गोल भूरे धब्बे जिन पर संकेंद्रित छल्ले (Target boards) बने होते हैं।",
        "treatment_hi": "मैंकोजेब 75% WP (डाइथेन एम-45) @ 600-800 ग्राम प्रति 200 लीटर पानी में मिलाकर 10-12 दिन के अंतराल पर छिड़कें।",
        "treatment_haryanvi": "टमाटर की निचली पत्तियां पै अगेती झुलसा आ गया सै। 600 ग्राम मैंकोजेब (M-45) 200 लीटर पाणी म मिलाकै बढ़िया छिड़काव करो।",
        "treatment_en": "Spray Mancozeb 75% WP (Dithane M-45) @ 600-800 g in 200 L water per acre at 10-12 day intervals."
    },
    {
        "id": "sugarcane_red_rot",
        "crop": "Sugarcane",
        "triggers": ["लाल", "सड़न", "शराब जैसी बदबू", "red rot", "lal sadan", "rot"],
        "disease": "Red Rot (लाल सड़न - Colletotrichum falcatum)",
        "severity": "CRITICAL",
        "symptoms_summary": "तीसरी-चौथी पत्ती सूखना, गन्ने को चीरने पर अंदर लाल गूदा व सफेद आड़े धब्बे तथा शराब जैसी खट्टी गंध।",
        "treatment_hi": "रोगी गन्नों को उखाड़कर नष्ट करें। खेत में पानी न रुकने दें। ट्राइकोडर्मा विरिडी (2.5 किग्रा) 100 किग्रा गोबर की खाद में मिलाकर खेत में डालें।",
        "treatment_haryanvi": "गन्ने म लाल सड़न का कैंसर रोग सै। रोगी गन्ने पाटो अर खेत म ट्राइकोडर्मा 2.5 किलो देसी खाद म मिलाकै बखेर द्यो।",
        "treatment_en": "Uproot infected clumps. Apply Trichoderma viride @ 2.5 kg enriched in 100 kg farmyard manure per acre."
    },
    {
        "id": "mustard_white_rust",
        "crop": "Mustard",
        "triggers": ["सफेद", "फफोले", "white", "rust", "safed", "chepa", "aphid"],
        "disease": "White Rust & Downy Mildew (सफेद रतुआ - Albugo candida)",
        "severity": "MODERATE",
        "symptoms_summary": "पत्तियों की निचली सतह पर सफेद या हल्के पीले उभरे हुए फफोले तथा पुष्पक्रम में विकृति।",
        "treatment_hi": "मेटालैक्सिल 8% + मैंकोजेब 64% WP (रिडोमिल गोल्ड) @ 500 ग्राम या मैंकोजेब @ 600 ग्राम प्रति 200 लीटर पानी में छिड़कें।",
        "treatment_haryanvi": "सरसों म सफेद रतुआ सै। 500 ग्राम रिडोमिल गोल्ड 200 लीटर पाणी म घोलकै छिड़क द्यो, चेपा भी खत्म हो ज्यागा।",
        "treatment_en": "Spray Metalaxyl 8% + Mancozeb 64% WP (Ridomil Gold) @ 500 g in 200 L water per acre."
    }
]

HARYANA_DISTRICTS = [
    "Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram",
    "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh",
    "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"
]


# ============================================================================
# Parsing Engine
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalizes text by stripping accents, lowering English, and removing punctuation."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[!?,.;:\"'()\[\]{}]+", " ", text)
    return text


def detect_crop(normalized_query: str) -> Optional[Dict[str, Any]]:
    """Identifies the agricultural crop mentioned in the voice query."""
    for crop_name, data in CROPS_LEXICON.items():
        for kw in data["keywords"]:
            pattern = r'\b' + re.escape(kw) + r'\b' if kw.isascii() else re.escape(kw)
            if re.search(pattern, normalized_query, re.IGNORECASE):
                return {
                    "crop_name": crop_name,
                    "hindi_name": data["hindi_name"],
                    "scientific_name": data["scientific_name"]
                }
    return None


def detect_district(normalized_query: str) -> Optional[str]:
    """Identifies any of the 22 Haryana districts mentioned."""
    for d in HARYANA_DISTRICTS:
        if d.lower() in normalized_query:
            return d
    return None


def match_symptom_or_disease(normalized_query: str, detected_crop: Optional[str]) -> Optional[Dict[str, Any]]:
    """Matches symptoms, pest descriptions, or disease names."""
    best_match = None
    max_score = 0

    for rule in SYMPTOM_DISEASE_RULES:
        # If crop is explicitly detected, prioritize matching rules for that crop
        crop_matches = (detected_crop is None) or (rule["crop"].lower() in detected_crop.lower())
        score = 0

        for trigger in rule["triggers"]:
            if trigger in normalized_query:
                score += 2 if crop_matches else 1

        if score > max_score and score > 0:
            max_score = score
            best_match = rule

    return best_match


def parse_voice_query(query_text: str, district_hint: Optional[str] = "Karnal") -> Dict[str, Any]:
    """
    Main entry point: Parses natural spoken voice query (Hindi, Haryanvi, Hinglish, or English)
    and returns a structured agronomic diagnosis, spoken dialect audio scripts, and CCS HAU prescriptions.
    """
    clean_text = normalize_text(query_text)
    
    # 1. Detect Crop
    crop_info = detect_crop(clean_text)
    detected_crop_name = crop_info["crop_name"] if crop_info else None
    
    # 2. Detect District
    district = detect_district(clean_text) or district_hint or "Karnal"
    
    # 3. Match Symptom / Pathology
    matched_rule = match_symptom_or_disease(clean_text, detected_crop_name)
    
    # 4. Resolve fallback if specific disease not clearly triggered
    if not matched_rule and crop_info:
        # General care for detected crop
        crop_key = crop_info["crop_name"]
        return {
            "status": "GENERAL_ADVICE",
            "query": query_text,
            "district": district,
            "crop": crop_info["crop_name"],
            "hindi_name": crop_info["hindi_name"],
            "disease_detected": None,
            "severity": "NORMAL",
            "spoken_hi": f"नमस्ते किसान भाई! आपकी {crop_info['hindi_name']} की फसल के लिए अनुशंसित पैकेज ऑफ प्रैक्टिसेज उपलब्ध है। यदि कोई पीलापन, कीट या सूखापन दिखे तो कृपया लक्षण बताएं।",
            "spoken_haryanvi": f"राम राम किसान भाई! थारी {crop_info['hindi_name']} खातर पूरी सलाह तैयार सै। फसल म कोई रोग या सुंडी दिखे तो फेर बोलकै बताओ।",
            "spoken_en": f"Hello farmer! We have general cultivation guidance for your {crop_info['crop_name']}. Please describe leaf spots or insect damage to get specific dosage.",
            "recommendation": "Maintain proper drainage, inspect lower leaves for fungal lesions, and submit a leaf photo for AI visual analysis.",
            "prescription": "No chemical spray needed currently. Monitor every 3-4 days.",
            "confidence": 0.85
        }
    
    if not matched_rule and not crop_info:
        # General query fallback
        return {
            "status": "UNRECOGNIZED",
            "query": query_text,
            "district": district,
            "crop": "General Crop",
            "hindi_name": "कृषि फसल",
            "disease_detected": None,
            "severity": "LOW",
            "spoken_hi": "राम-राम किसान भाई! कृपया अपनी फसल का नाम जैसे गेहूं, धान, नरमा, या टमाटर और उसमें दिखने वाले लक्षण बोलकर बताएं।",
            "spoken_haryanvi": "राम राम भाई! थारी फसल का नाम अर लक्षण साफ-साफ बताओ, जैसै कनक म पीलापन या नरमा म सुंडी।",
            "spoken_en": "Please mention your crop name (e.g. Wheat, Rice, Cotton, Tomato) and visible symptoms like yellowing, rot, or pests.",
            "recommendation": "Say e.g.: 'मेरी कनक में पीला रतुआ है' or 'नरमा में गुलाबी सूंढी का क्या इलाज है?'",
            "prescription": "Awaiting clear crop and symptom description.",
            "confidence": 0.40
        }

    # 5. Full Disease Diagnosis & Remedy Found
    final_crop = crop_info["hindi_name"] if crop_info else matched_rule["crop"]
    
    return {
        "status": "DIAGNOSIS_MATCHED",
        "query": query_text,
        "district": district,
        "crop": matched_rule["crop"],
        "hindi_crop_name": final_crop,
        "disease_detected": matched_rule["disease"],
        "severity": matched_rule["severity"],
        "symptoms": matched_rule["symptoms_summary"],
        "spoken_hi": f"किसान भाई, आपकी {final_crop} में {matched_rule['disease']} के लक्षण हैं। समाधान: {matched_rule['treatment_hi']}",
        "spoken_haryanvi": f"राम राम किसान भाई! {matched_rule['treatment_haryanvi']}",
        "spoken_en": f"Farmer alert: We identified {matched_rule['disease']} in your {matched_rule['crop']}. Solution: {matched_rule['treatment_en']}",
        "recommendation": matched_rule["treatment_hi"],
        "recommendation_haryanvi": matched_rule["treatment_haryanvi"],
        "recommendation_en": matched_rule["treatment_en"],
        "prescription": matched_rule["treatment_hi"],
        "confidence": 0.94
    }
