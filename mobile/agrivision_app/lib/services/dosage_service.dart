class DosageResult {
  final double acreage;
  final double waterVolumeLiters;
  final double knapsackTanks15L;
  final String chemicalNameEn;
  final String chemicalNameHi;
  final String chemicalAmount;
  final String organicNameEn;
  final String organicNameHi;
  final String organicAmount;
  final List<String> safetyEquipmentEn;
  final List<String> safetyEquipmentHi;
  final int phiDays;

  DosageResult({
    required this.acreage,
    required this.waterVolumeLiters,
    required this.knapsackTanks15L,
    required this.chemicalNameEn,
    required this.chemicalNameHi,
    required this.chemicalAmount,
    required this.organicNameEn,
    required this.organicNameHi,
    required this.organicAmount,
    required this.safetyEquipmentEn,
    required this.safetyEquipmentHi,
    required this.phiDays,
  });
}

class DosageService {
  static DosageResult calculate({
    required String className,
    required double acres,
  }) {
    // 200 Liters of water per acre standard for vegetable foliage
    final double water = acres * 200.0;
    final double tanks = water / 15.0;

    final lower = className.toLowerCase();

    if (lower.contains('healthy')) {
      return DosageResult(
        acreage: acres,
        waterVolumeLiters: water,
        knapsackTanks15L: tanks,
        chemicalNameEn: 'None (Crop is healthy)',
        chemicalNameHi: 'किसी रासायनिक दवा की आवश्यकता नहीं है',
        chemicalAmount: '0 kg',
        organicNameEn: 'Pure Neem Oil 3000 ppm (Preventive protective coating)',
        organicNameHi: 'नीम का तेल 3000 ppm (सुरक्षात्मक छिड़काव)',
        organicAmount: '${(water * 3.0 / 1000).toStringAsFixed(2)} Liters',
        safetyEquipmentEn: ['Rubber Gloves', 'Field Sun Hat'],
        safetyEquipmentHi: ['रबर के दस्ताने', 'धूप से बचाव की टोपी'],
        phiDays: 0,
      );
    } else if (lower.contains('early_blight') || lower.contains('early blight')) {
      final double chemKg = (water * 2.5) / 1000.0;
      final double neemL = (water * 5.0) / 1000.0;
      return DosageResult(
        acreage: acres,
        waterVolumeLiters: water,
        knapsackTanks15L: tanks,
        chemicalNameEn: 'Mancozeb 75% WP (or Azoxystrobin 23% SC)',
        chemicalNameHi: 'मैंकोजेब 75% WP (या एज़ोक्सीस्ट्रोबिन 23% SC)',
        chemicalAmount: '${chemKg.toStringAsFixed(2)} kg (or ${(water * 1.0).toStringAsFixed(0)} ml Azoxy)',
        organicNameEn: 'Trichoderma harzianum + Cold-pressed Neem Oil',
        organicNameHi: 'ट्राइकोडर्मा हरजिएनम + नीम का तेल',
        organicAmount: '${chemKg.toStringAsFixed(2)} kg Trichoderma + ${neemL.toStringAsFixed(2)} L Neem Oil',
        safetyEquipmentEn: ['N95 Chemical Mask', 'Nitrile Gloves', 'Goggles', 'Rubber Boots'],
        safetyEquipmentHi: ['N95 मास्क', 'नाइट्राइल दस्ताने', 'सुरक्षा चश्मा', 'गमबूट्स'],
        phiDays: 7,
      );
    } else if (lower.contains('late_blight') || lower.contains('late blight')) {
      final double chemKg = (water * 2.5) / 1000.0;
      return DosageResult(
        acreage: acres,
        waterVolumeLiters: water,
        knapsackTanks15L: tanks,
        chemicalNameEn: 'Ridomil MZ (Metalaxyl 8% + Mancozeb 64% WP)',
        chemicalNameHi: 'रिडोमिल MZ (मेटालेक्सिल + मैंकोजेब)',
        chemicalAmount: '${chemKg.toStringAsFixed(2)} kg',
        organicNameEn: 'Copper Hydroxide 77% WP (or Bordeaux Mixture 1%)',
        organicNameHi: 'कॉपर हाइड्रोक्साइड (या बोर्डो मिश्रण 1%)',
        organicAmount: '${(water * 2.0 / 1000).toStringAsFixed(2)} kg',
        safetyEquipmentEn: ['N95 Chemical Mask', 'Nitrile Gloves', 'Goggles', 'Full Sleeve Apron'],
        safetyEquipmentHi: ['N95 मास्क', 'दस्ताने', 'चश्मा', 'सुरक्षात्मक एप्रन'],
        phiDays: 7,
      );
    } else if (lower.contains('bacterial')) {
      final double cocKg = (water * 2.5) / 1000.0;
      final double streptoG = water * 0.05;
      return DosageResult(
        acreage: acres,
        waterVolumeLiters: water,
        knapsackTanks15L: tanks,
        chemicalNameEn: 'Copper Oxychloride (50% WP) + Streptocycline',
        chemicalNameHi: 'कॉपर ऑक्सीक्लोराइड (50% WP) + स्ट्रेप्टोसाइक्लिन',
        chemicalAmount: '${cocKg.toStringAsFixed(2)} kg COC + ${streptoG.toStringAsFixed(1)} g Streptocycline',
        organicNameEn: 'Bacillus subtilis bio-agent + Neem formulation',
        organicNameHi: 'बैसिलस सबटिलिस + नीम फॉर्मूलेशन',
        organicAmount: '${(water * 2.5 / 1000).toStringAsFixed(2)} kg Bacillus + ${(water * 4 / 1000).toStringAsFixed(2)} L Neem',
        safetyEquipmentEn: ['Chemical Vapor Respirator', 'Rubber Gloves', 'Eye Protection'],
        safetyEquipmentHi: ['केमिकल रेस्पिरेटर मास्क', 'रबर दस्ताने', 'आंखों का चश्मा'],
        phiDays: 5,
      );
    } else if (lower.contains('spider_mite') || lower.contains('mite')) {
      final double abamectinMl = water * 0.5;
      final double neemL = (water * 5.0) / 1000.0;
      return DosageResult(
        acreage: acres,
        waterVolumeLiters: water,
        knapsackTanks15L: tanks,
        chemicalNameEn: 'Abamectin 1.9% EC (or Spiromesifen 22.9% SC)',
        chemicalNameHi: 'एबामेक्टिन 1.9% EC (या स्पाइरोमेसिफेन)',
        chemicalAmount: '${abamectinMl.toStringAsFixed(0)} ml Abamectin',
        organicNameEn: 'Neem Oil (10,000 ppm) + Horticultural Soap',
        organicNameHi: 'नीम का तेल + जैविक साबुन घोल',
        organicAmount: '${neemL.toStringAsFixed(2)} L Neem Oil + ${(water * 2 / 1000).toStringAsFixed(2)} L Soap',
        safetyEquipmentEn: ['Face Shield', 'Nitrile Gloves', 'Waterproof Apron'],
        safetyEquipmentHi: ['फेस शील्ड', 'नाइट्राइल दस्ताने', 'वाटरप्रूफ एप्रन'],
        phiDays: 3,
      );
    } else {
      // General broad spectrum
      final double chemKg = (water * 2.5) / 1000.0;
      final double neemL = (water * 4.0) / 1000.0;
      return DosageResult(
        acreage: acres,
        waterVolumeLiters: water,
        knapsackTanks15L: tanks,
        chemicalNameEn: 'Mancozeb 75% WP or Chlorothalonil 75% WP',
        chemicalNameHi: 'मैंकोजेब 75% WP या क्लोरोथैलोनिल 75% WP',
        chemicalAmount: '${chemKg.toStringAsFixed(2)} kg',
        organicNameEn: 'Neem Formulation (10,000 ppm) + Trichoderma viride',
        organicNameHi: 'नीम फॉर्मूलेशन + ट्राइकोडर्मा विरिडी',
        organicAmount: '${neemL.toStringAsFixed(2)} L Neem + ${chemKg.toStringAsFixed(2)} kg Trichoderma',
        safetyEquipmentEn: ['N95 Chemical Mask', 'Gloves', 'Eye Goggles'],
        safetyEquipmentHi: ['N95 मास्क', 'दस्ताने', 'चश्मा'],
        phiDays: 5,
      );
    }
  }
}
