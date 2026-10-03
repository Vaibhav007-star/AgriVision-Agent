import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/dosage_service.dart';

class DosageCalculatorScreen extends StatefulWidget {
  final bool isHindi;

  const DosageCalculatorScreen({Key? key, required this.isHindi}) : super(key: key);

  @override
  State<DosageCalculatorScreen> createState() => _DosageCalculatorScreenState();
}

class _DosageCalculatorScreenState extends State<DosageCalculatorScreen> {
  double _acreage = 1.0;
  String _selectedClass = 'Tomato_Early_blight';

  final List<Map<String, String>> _diseaseOptions = [
    {'key': 'Tomato_Early_blight', 'en': 'Tomato - Early Blight', 'hi': 'टमाटर - अगेती झुलसा'},
    {'key': 'Tomato_Late_blight', 'en': 'Tomato - Late Blight', 'hi': 'टमाटर - पछेती झुलसा'},
    {'key': 'Tomato_Bacterial_spot', 'en': 'Tomato - Bacterial Spot', 'hi': 'टमाटर - जीवाणु धब्बा'},
    {'key': 'Tomato_Septoria_leaf_spot', 'en': 'Tomato - Septoria Leaf Spot', 'hi': 'टमाटर - सेप्टोरिया पत्ती धब्बा'},
    {'key': 'Tomato_Spider_mites_Two_spotted_spider_mite', 'en': 'Tomato - Spider Mites', 'hi': 'टमाटर - लाल मकड़ी कीट'},
    {'key': 'Tomato_Leaf_Mold', 'en': 'Tomato - Leaf Mold', 'hi': 'टमाटर - पत्ती फफूंद'},
    {'key': 'Tomato__Target_Spot', 'en': 'Tomato - Target Spot', 'hi': 'टमाटर - टारगेट स्पॉट'},
    {'key': 'Tomato_healthy', 'en': 'Tomato - Healthy (Preventive)', 'hi': 'टमाटर - स्वस्थ (सुरक्षात्मक)'},
    {'key': 'Potato___Early_blight', 'en': 'Potato - Early Blight', 'hi': 'आलू - अगेती झुलसा'},
    {'key': 'Potato___Late_blight', 'en': 'Potato - Late Blight', 'hi': 'आलू - पछेती झुलसा'},
    {'key': 'Potato___healthy', 'en': 'Potato - Healthy (Preventive)', 'hi': 'आलू - स्वस्थ (सुरक्षात्मक)'},
    {'key': 'Pepper__bell___Bacterial_spot', 'en': 'Pepper - Bacterial Spot', 'hi': 'शिमला मिर्च - जीवाणु धब्बा'},
    {'key': 'Pepper__bell___healthy', 'en': 'Pepper - Healthy (Preventive)', 'hi': 'शिमला मिर्च - स्वस्थ (सुरक्षात्मक)'},
  ];

  @override
  Widget build(BuildContext context) {
    final bool hi = widget.isHindi;
    final dosage = DosageService.calculate(
      className: _selectedClass,
      acres: _acreage,
    );

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7F4),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1B5E20),
        title: Text(
          hi ? 'खेत स्प्रे व दवा कैलकुलेटर' : 'Field Spray & Dosage Tool',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 18, color: Colors.white),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Crop & Disease Selector
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFA5D6A7)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    hi ? 'फसल एवं रोग चुनें:' : 'Select Crop & Disease:',
                    style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.grey.shade700),
                  ),
                  DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: _selectedClass,
                      isExpanded: true,
                      icon: const Icon(Icons.keyboard_arrow_down_rounded, color: Color(0xFF2E7D32)),
                      onChanged: (String? newValue) {
                        if (newValue != null) {
                          setState(() {
                            _selectedClass = newValue;
                          });
                        }
                      },
                      items: _diseaseOptions.map((opt) {
                        return DropdownMenuItem<String>(
                          value: opt['key'],
                          child: Text(
                            hi ? opt['hi']! : opt['en']!,
                            style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 13),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Acreage Selector Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFA5D6A7)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        hi ? 'खेत का आकार:' : 'Field Acreage:',
                        style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w600),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE8F5E9),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          '${_acreage.toStringAsFixed(1)} ${hi ? "एकड़" : "Acres"} (${(_acreage * 1.6).toStringAsFixed(1)} ${hi ? "बीघा" : "Bigha"})',
                          style: GoogleFonts.poppins(
                            fontWeight: FontWeight.w700,
                            color: const Color(0xFF2E7D32),
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                  Slider(
                    value: _acreage,
                    min: 0.5,
                    max: 10.0,
                    divisions: 19,
                    activeColor: const Color(0xFF2E7D32),
                    inactiveColor: const Color(0xFFC8E6C9),
                    onChanged: (val) {
                      setState(() {
                        _acreage = val;
                      });
                    },
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Tank & Water Stats
            Row(
              children: [
                Expanded(
                  child: _buildMetricTile(
                    icon: Icons.water_drop_rounded,
                    title: hi ? 'पानी की आवश्यकता' : 'Water Volume',
                    value: '${dosage.waterVolumeLiters.toStringAsFixed(0)} Liters',
                    subtitle: hi ? '200 लीटर प्रति एकड़' : '200 L per acre',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildMetricTile(
                    icon: Icons.backpack_rounded,
                    title: hi ? 'स्प्रेयर पंप संख्या' : 'Backpack Tanks',
                    value: '${dosage.knapsackTanks15L.toStringAsFixed(1)} Pumps',
                    subtitle: hi ? '15 लीटर प्रति पंप' : '15L standard tank',
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Chemical Requirement Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFBBDEFB)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.science_rounded, color: Color(0xFF1976D2), size: 22),
                      const SizedBox(width: 8),
                      Text(
                        hi ? 'रासायनिक कीटनाशक/फफूंदनाशक मात्रा' : 'Chemical Formulation Needed',
                        style: GoogleFonts.poppins(
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: const Color(0xFF1565C0),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    hi ? dosage.chemicalNameHi : dosage.chemicalNameEn,
                    style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE3F2FD),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      hi
                          ? 'कुल खेत के लिए आवश्यकता: ${dosage.chemicalAmount}'
                          : 'Total Required for Field: ${dosage.chemicalAmount}',
                      style: GoogleFonts.poppins(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                        color: const Color(0xFF0D47A1),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            // Organic Requirement Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFC8E6C9)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.spa_rounded, color: Color(0xFF388E3C), size: 22),
                      const SizedBox(width: 8),
                      Text(
                        hi ? 'जैविक विकल्प मात्रा' : 'Organic / Bio Formulation Needed',
                        style: GoogleFonts.poppins(
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: const Color(0xFF2E7D32),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    hi ? dosage.organicNameHi : dosage.organicNameEn,
                    style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8F5E9),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      hi
                          ? 'कुल जैविक मात्रा: ${dosage.organicAmount}'
                          : 'Total Organic Required: ${dosage.organicAmount}',
                      style: GoogleFonts.poppins(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                        color: const Color(0xFF1B5E20),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            // Safety Equipment Checklist
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFFFCC80)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.security_rounded, color: Color(0xFFE65100), size: 22),
                      const SizedBox(width: 8),
                      Text(
                        hi ? 'आवश्यक सुरक्षा उपकरण (PPE Checklist)' : 'Mandatory Safety Gear (PPE)',
                        style: GoogleFonts.poppins(
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                          color: const Color(0xFFBF360C),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: (hi ? dosage.safetyEquipmentHi : dosage.safetyEquipmentEn).map((gear) {
                      return Chip(
                        backgroundColor: const Color(0xFFFFF3E0),
                        label: Text(
                          gear,
                          style: GoogleFonts.poppins(fontSize: 11, fontWeight: FontWeight.w500),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricTile({
    required IconData icon,
    required String title,
    required String value,
    required String subtitle,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE0E0E0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: const Color(0xFF2E7D32), size: 24),
          const SizedBox(height: 8),
          Text(title, style: GoogleFonts.poppins(fontSize: 11, color: Colors.grey.shade600)),
          Text(
            value,
            style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: const Color(0xFF1B5E20)),
          ),
          const SizedBox(height: 2),
          Text(subtitle, style: GoogleFonts.poppins(fontSize: 10, color: Colors.grey.shade500)),
        ],
      ),
    );
  }
}
