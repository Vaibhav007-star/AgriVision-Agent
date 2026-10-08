import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/haryana_offline_block.dart';
import '../services/offline_agronomy_service.dart';

class HaryanaOfflineAdvisorScreen extends StatefulWidget {
  final bool isHindi;

  const HaryanaOfflineAdvisorScreen({super.key, required this.isHindi});

  @override
  State<HaryanaOfflineAdvisorScreen> createState() => _HaryanaOfflineAdvisorScreenState();
}

class _HaryanaOfflineAdvisorScreenState extends State<HaryanaOfflineAdvisorScreen> {
  final OfflineAgronomyService _service = OfflineAgronomyService();
  bool _isLoading = true;
  String _selectedDistrict = 'Karnal';
  String? _selectedBlock;
  String? _selectedDiseaseKey;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      await _service.initialize();
      final blocks = _service.getBlocksForDistrict(_selectedDistrict);
      setState(() {
        _isLoading = false;
        if (blocks.isNotEmpty) {
          _selectedBlock = blocks.first.blockName;
          _selectedDiseaseKey = blocks.first.symptomChecklist.keys.isNotEmpty
              ? blocks.first.symptomChecklist.keys.first
              : null;
        }
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool hi = widget.isHindi;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7F4),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1B5E20),
        elevation: 0,
        title: Text(
          hi ? 'हरियाणा ब्लॉक सलाहकार (100% ऑफलाइन)' : 'Haryana Block Agronomy (100% Offline)',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 17, color: Colors.white),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Offline Status Badge
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8F5E9),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFA5D6A7)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.offline_pin_rounded, color: Color(0xFF2E7D32), size: 18),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            hi
                                ? 'पूर्णतः ऑफलाइन: हरियाणा के 22 जिलों व सभी खंडों की स्थानीय कृषि जानकारी'
                                : '100% Offline: Localized agronomy for all 22 Haryana districts & blocks',
                            style: GoogleFonts.poppins(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: const Color(0xFF1B5E20),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // District & Block Selection Card
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.04),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          hi ? 'अपना जिला और खंड (Block) चुनें:' : 'Select District & Block:',
                          style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 12),
                        // District Dropdown
                        DropdownButtonFormField<String>(
                          value: _selectedDistrict,
                          decoration: InputDecoration(
                            labelText: hi ? 'जिला (District)' : 'District',
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          ),
                          items: _service.getDistricts().map((d) {
                            return DropdownMenuItem<String>(
                              value: d,
                              child: Text(d, style: GoogleFonts.poppins(fontSize: 14)),
                            );
                          }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              setState(() {
                                _selectedDistrict = val;
                                final blocks = _service.getBlocksForDistrict(val);
                                _selectedBlock = blocks.isNotEmpty ? blocks.first.blockName : null;
                                _selectedDiseaseKey = (blocks.isNotEmpty &&
                                        blocks.first.symptomChecklist.keys.isNotEmpty)
                                    ? blocks.first.symptomChecklist.keys.first
                                    : null;
                              });
                            }
                          },
                        ),

                        const SizedBox(height: 12),

                        // Block Dropdown
                        if (_selectedDistrict.isNotEmpty)
                          DropdownButtonFormField<String>(
                            value: _selectedBlock,
                            decoration: InputDecoration(
                              labelText: hi ? 'खंड / ब्लॉक (Block)' : 'Administrative Block',
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                            ),
                            items: _service.getBlocksForDistrict(_selectedDistrict).map((b) {
                              return DropdownMenuItem<String>(
                                value: b.blockName,
                                child: Text(b.blockName, style: GoogleFonts.poppins(fontSize: 14)),
                              );
                            }).toList(),
                            onChanged: (val) {
                              if (val != null) {
                                setState(() {
                                  _selectedBlock = val;
                                  final block = _service.getBlock(_selectedDistrict, val);
                                  _selectedDiseaseKey = (block != null &&
                                          block.symptomChecklist.keys.isNotEmpty)
                                      ? block.symptomChecklist.keys.first
                                      : null;
                                });
                              }
                            },
                          ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Block Profile & Dialect Card
                  if (_selectedBlock != null) ...[
                    _buildBlockDetailCard(hi),
                    const SizedBox(height: 16),
                    _buildSymptomTriageCard(hi),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildBlockDetailCard(bool hi) {
    final block = _service.getBlock(_selectedDistrict, _selectedBlock!);
    if (block == null) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: const BoxDecoration(
                  color: Color(0xFFE8F5E9),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.record_voice_over_rounded, color: Color(0xFF2E7D32), size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${block.blockName}, ${block.districtName}',
                      style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      '${hi ? "स्थानीय बोली (Dialect): " : "Local Dialect: "}${block.primaryDialect}',
                      style: GoogleFonts.poppins(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFFEF6C00),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const Divider(height: 24),

          // Primary Crops (Vernacular names)
          Text(
            hi ? 'मुख्य स्थानीय फसलें (स्थानीय नाम):' : 'Primary Regional Crops:',
            style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.grey.shade800),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: block.primaryCrops.map((crop) {
              return Chip(
                backgroundColor: const Color(0xFFE8F5E9),
                avatar: const Icon(Icons.eco, size: 16, color: Color(0xFF2E7D32)),
                label: Text(
                  crop,
                  style: GoogleFonts.poppins(fontSize: 11, fontWeight: FontWeight.w600, color: const Color(0xFF1B5E20)),
                ),
              );
            }).toList(),
          ),

          const SizedBox(height: 12),

          // Top 3 Local Diseases
          Text(
            hi ? 'शीर्ष 3 स्थानीय रोग व कीट:' : 'Top 3 Regional Pathogens/Pests:',
            style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.grey.shade800),
          ),
          const SizedBox(height: 8),
          Column(
            children: block.top3Diseases.map((dis) {
              return Container(
                margin: const EdgeInsets.only(bottom: 6),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF8E1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFFFE082)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.bug_report, size: 16, color: Color(0xFFF57F17)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        dis,
                        style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w500, color: const Color(0xFFE65100)),
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildSymptomTriageCard(bool hi) {
    final block = _service.getBlock(_selectedDistrict, _selectedBlock!);
    if (block == null || block.symptomChecklist.isEmpty) return const SizedBox.shrink();

    final diseaseKeys = block.symptomChecklist.keys.toList();
    final activeKey = _selectedDiseaseKey ?? diseaseKeys.first;
    final symptomChain = block.symptomChecklist[activeKey] ?? '';
    final approvedSolution = block.approvedPesticideSolutions[activeKey] ?? '';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.checklist_rtl_rounded, color: Color(0xFF1B5E20), size: 22),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  hi ? 'ऑफ़लाइन लक्षण जांच व सटीक निदान' : 'Offline Symptom Checklist Triage',
                  style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            hi
                ? 'लक्षणों का क्रम देखकर रोग पहचानें एवं HAU अनुमोदित खुराक देखें:'
                : 'Follow the diagnostic chain below to verify symptoms without internet:',
            style: GoogleFonts.poppins(fontSize: 12, color: Colors.grey.shade600),
          ),
          const SizedBox(height: 14),

          // Disease Selector Tabs
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: diseaseKeys.map((k) {
                final isSelected = k == activeKey;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(
                      k.replaceAll('_', ' '),
                      style: GoogleFonts.poppins(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: isSelected ? Colors.white : Colors.black87,
                      ),
                    ),
                    selected: isSelected,
                    selectedColor: const Color(0xFF2E7D32),
                    backgroundColor: const Color(0xFFF1F8E9),
                    onSelected: (val) {
                      if (val) setState(() => _selectedDiseaseKey = k);
                    },
                  ),
                );
              }).toList(),
            ),
          ),

          const SizedBox(height: 16),

          // Diagnostic Chain Steps
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFE8F5E9),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFC8E6C9)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.route_rounded, color: Color(0xFF2E7D32), size: 18),
                    const SizedBox(width: 6),
                    Text(
                      hi ? 'निदान क्रम (Diagnostic Chain):' : 'Linear Diagnostic Chain:',
                      style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.bold, color: const Color(0xFF1B5E20)),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  symptomChain,
                  style: GoogleFonts.poppins(fontSize: 13, height: 1.5, color: const Color(0xFF2E7D32)),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // CCS HAU Approved Pesticide Solution Box
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFFFF3E0),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFFFCC80)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.verified, color: Color(0xFFE65100), size: 18),
                    const SizedBox(width: 6),
                    Text(
                      hi
                          ? 'HAU हिसार अनुमोदित दवा व प्रति एकड़ खुराक:'
                          : 'CCS HAU Approved Solution & Dosage / Acre:',
                      style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.bold, color: const Color(0xFFE65100)),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  approvedSolution,
                  style: GoogleFonts.poppins(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    height: 1.5,
                    color: const Color(0xFFBF360C),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

