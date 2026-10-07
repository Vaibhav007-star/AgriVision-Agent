import 'dart:io';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/disease_info.dart';
import '../services/dosage_service.dart';

class ResultScreen extends StatefulWidget {
  final DiagnosisResult result;
  final bool isHindi;

  const ResultScreen({
    super.key,
    required this.result,
    required this.isHindi,
  });

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  double _acreage = 1.0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'high':
        return Colors.red.shade700;
      case 'moderate':
        return Colors.orange.shade800;
      case 'none':
        return Colors.green.shade700;
      default:
        return Colors.blue.shade700;
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool hi = widget.isHindi;
    final res = widget.result;
    final detail = res.detail;
    final topPred = res.topPrediction;
    final dosage = DosageService.calculate(
      className: topPred.className,
      acres: _acreage,
    );

    final double confPct = (topPred.confidence * 100).clamp(0.0, 100.0);

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7F4),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xFF1B5E20),
        title: Text(
          hi ? 'निदान एवं परामर्श रिपोर्ट' : 'Diagnosis & Field Advisory',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.w600,
            fontSize: 18,
            color: Colors.white,
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Top Card: Image + Disease Name + Confidence
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  ClipRRect(
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                    child: Image.file(
                      File(res.imagePath),
                      height: 190,
                      width: double.infinity,
                      fit: BoxFit.cover,
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFFE8F5E9),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                hi ? detail.cropHi : detail.cropEn,
                                style: GoogleFonts.poppins(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 13,
                                  color: const Color(0xFF2E7D32),
                                ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: _getSeverityColor(detail.severity).withValues(alpha: 0.12),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                hi
                                    ? 'गंभीरता: ${detail.severity}'
                                    : 'Severity: ${detail.severity}',
                                style: GoogleFonts.poppins(
                                  fontWeight: FontWeight.w700,
                                  fontSize: 12,
                                  color: _getSeverityColor(detail.severity),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          hi ? detail.diseaseHi : detail.diseaseEn,
                          style: GoogleFonts.poppins(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                            color: const Color(0xFF212121),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          hi
                              ? 'रोगज़नक़: ${detail.pathogenType}'
                              : 'Pathogen: ${detail.pathogenType}',
                          style: GoogleFonts.poppins(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                          ),
                        ),
                        const SizedBox(height: 12),
                        // Confidence Bar
                        Row(
                          children: [
                            Text(
                              hi ? 'सटीकता:' : 'Confidence:',
                              style: GoogleFonts.poppins(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: const Color(0xFF424242),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(6),
                                child: LinearProgressIndicator(
                                  value: confPct / 100.0,
                                  minHeight: 10,
                                  backgroundColor: Colors.grey.shade200,
                                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF2E7D32)),
                                ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Text(
                              '${confPct.toStringAsFixed(1)}%',
                              style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w700,
                                fontSize: 14,
                                color: const Color(0xFF2E7D32),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Top-3 Predictions Collapsible Card
            Theme(
              data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFE0E0E0)),
                ),
                child: ExpansionTile(
                  leading: const Icon(Icons.analytics_rounded, color: Color(0xFF2E7D32)),
                  title: Text(
                    hi ? 'शीर्ष 3 संभावित रोग (Top-3 Model Ranking)' : 'Top-3 Predictions Breakdown',
                    style: GoogleFonts.poppins(
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                      color: const Color(0xFF212121),
                    ),
                  ),
                  children: res.top3.map((pred) {
                    final pPct = (pred.confidence * 100).toStringAsFixed(1);
                    return ListTile(
                      dense: true,
                      title: Text(
                        pred.className.replaceAll('_', ' '),
                        style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w500),
                      ),
                      trailing: Text(
                        '$pPct%',
                        style: GoogleFonts.poppins(
                          fontWeight: FontWeight.w700,
                          fontSize: 12,
                          color: const Color(0xFF2E7D32),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Field Dosage Calculator Slider
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
                        hi ? 'खेत का क्षेत्रफल (एकड़)' : 'Field Acreage Slider',
                        style: GoogleFonts.poppins(
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: const Color(0xFF1B5E20),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE8F5E9),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          '${_acreage.toStringAsFixed(1)} ${hi ? "एकड़" : "Acres"}',
                          style: GoogleFonts.poppins(
                            fontWeight: FontWeight.w700,
                            color: const Color(0xFF2E7D32),
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
                  Row(
                    children: [
                      _buildDosageStat(
                        Icons.water_drop_rounded,
                        hi ? 'कुल पानी' : 'Water Req.',
                        '${dosage.waterVolumeLiters.toStringAsFixed(0)} L',
                      ),
                      const SizedBox(width: 8),
                      _buildDosageStat(
                        Icons.backpack_rounded,
                        hi ? '15L पंप' : '15L Tanks',
                        dosage.knapsackTanks15L.toStringAsFixed(1),
                      ),
                      const SizedBox(width: 8),
                      _buildDosageStat(
                        Icons.timer_rounded,
                        hi ? 'PHI प्रतीक्षा' : 'Safe PHI',
                        '${dosage.phiDays} ${hi ? "दिन" : "Days"}',
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Tab Bar: Chemical, Organic, Prevention
            Container(
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(12),
              ),
              child: TabBar(
                controller: _tabController,
                indicator: BoxDecoration(
                  color: const Color(0xFF2E7D32),
                  borderRadius: BorderRadius.circular(12),
                ),
                labelColor: Colors.white,
                unselectedLabelColor: const Color(0xFF424242),
                labelStyle: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 12),
                tabs: [
                  Tab(text: hi ? 'रासायनिक उपचार' : 'Chemical'),
                  Tab(text: hi ? 'जैविक समाधान' : 'Organic'),
                  Tab(text: hi ? 'रोकथाम उपाय' : 'Prevention'),
                ],
              ),
            ),

            const SizedBox(height: 12),

            // Tab View content
            SizedBox(
              height: 260,
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Chemical Tab
                  _buildAdvisoryCard(
                    title: hi ? detail.chemicalTreatment.nameHi : detail.chemicalTreatment.nameEn,
                    dosage: hi
                        ? 'खुराक: ${detail.chemicalTreatment.dosagePerLiter}'
                        : 'Dosage: ${detail.chemicalTreatment.dosagePerLiter}',
                    fieldQuantity: hi
                        ? 'खेत हेतु कुल मात्रा: ${dosage.chemicalAmount}'
                        : 'Total Field Requirement: ${dosage.chemicalAmount}',
                    extra: hi
                        ? 'छिड़काव अंतराल: ${detail.chemicalTreatment.sprayIntervalDays}'
                        : 'Interval: ${detail.chemicalTreatment.sprayIntervalDays}',
                    icon: Icons.science_rounded,
                    color: Colors.blue.shade700,
                  ),

                  // Organic Tab
                  _buildAdvisoryCard(
                    title: hi ? detail.organicTreatment.nameHi : detail.organicTreatment.nameEn,
                    dosage: hi
                        ? 'खुराक: ${detail.organicTreatment.dosagePerLiter}'
                        : 'Dosage: ${detail.organicTreatment.dosagePerLiter}',
                    fieldQuantity: hi
                        ? 'खेत हेतु कुल मात्रा: ${dosage.organicAmount}'
                        : 'Total Field Requirement: ${dosage.organicAmount}',
                    extra: hi
                        ? (detail.organicTreatment.notesHi ?? '')
                        : (detail.organicTreatment.notesEn ?? ''),
                    icon: Icons.spa_rounded,
                    color: Colors.green.shade700,
                  ),

                  // Prevention Tab
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFE0E0E0)),
                    ),
                    child: ListView(
                      physics: const BouncingScrollPhysics(),
                      children: (hi ? detail.preventionHi : detail.preventionEn).map((tip) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(Icons.check_circle_rounded, color: Color(0xFF2E7D32), size: 18),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  tip,
                                  style: GoogleFonts.poppins(fontSize: 12, color: const Color(0xFF424242)),
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildDosageStat(IconData icon, String title, String value) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
        decoration: BoxDecoration(
          color: const Color(0xFFF1F8E9),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Column(
          children: [
            Icon(icon, size: 18, color: const Color(0xFF2E7D32)),
            const SizedBox(height: 4),
            Text(
              title,
              style: GoogleFonts.poppins(fontSize: 10, color: Colors.grey.shade700),
              textAlign: TextAlign.center,
            ),
            Text(
              value,
              style: GoogleFonts.poppins(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: const Color(0xFF1B5E20),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAdvisoryCard({
    required String title,
    required String dosage,
    required String fieldQuantity,
    required String extra,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE0E0E0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: GoogleFonts.poppins(
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                    color: const Color(0xFF212121),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(dosage, style: GoogleFonts.poppins(fontSize: 12, color: const Color(0xFF424242))),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              fieldQuantity,
              style: GoogleFonts.poppins(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ),
          if (extra.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(extra, style: GoogleFonts.poppins(fontSize: 11, color: Colors.grey.shade700)),
          ],
        ],
      ),
    );
  }
}
