class TreatmentInfo {
  final String nameEn;
  final String nameHi;
  final String dosagePerLiter;
  final String sprayIntervalDays;
  final int phiDays;
  final String? notesEn;
  final String? notesHi;

  TreatmentInfo({
    required this.nameEn,
    required this.nameHi,
    required this.dosagePerLiter,
    required this.sprayIntervalDays,
    required this.phiDays,
    this.notesEn,
    this.notesHi,
  });

  factory TreatmentInfo.fromJson(Map<String, dynamic> json) {
    return TreatmentInfo(
      nameEn: json['name_en'] ?? '',
      nameHi: json['name_hi'] ?? '',
      dosagePerLiter: json['dosage_per_liter'] ?? '',
      sprayIntervalDays: json['spray_interval_days'] ?? '',
      phiDays: json['phi_days'] ?? 0,
      notesEn: json['notes_en'],
      notesHi: json['notes_hi'],
    );
  }
}

class DiseaseDetail {
  final String cropEn;
  final String cropHi;
  final String diseaseEn;
  final String diseaseHi;
  final bool isHealthy;
  final String severity;
  final String pathogenType;
  final String symptomsEn;
  final String symptomsHi;
  final TreatmentInfo chemicalTreatment;
  final TreatmentInfo organicTreatment;
  final List<String> preventionEn;
  final List<String> preventionHi;

  DiseaseDetail({
    required this.cropEn,
    required this.cropHi,
    required this.diseaseEn,
    required this.diseaseHi,
    required this.isHealthy,
    required this.severity,
    required this.pathogenType,
    required this.symptomsEn,
    required this.symptomsHi,
    required this.chemicalTreatment,
    required this.organicTreatment,
    required this.preventionEn,
    required this.preventionHi,
  });

  factory DiseaseDetail.fromJson(Map<String, dynamic> json) {
    return DiseaseDetail(
      cropEn: json['crop_en'] ?? 'Unknown',
      cropHi: json['crop_hi'] ?? 'अज्ञात',
      diseaseEn: json['disease_en'] ?? 'Unknown',
      diseaseHi: json['disease_hi'] ?? 'अज्ञात',
      isHealthy: json['is_healthy'] ?? false,
      severity: json['severity'] ?? 'Moderate',
      pathogenType: json['pathogen_type'] ?? 'Unknown',
      symptomsEn: json['symptoms_en'] ?? '',
      symptomsHi: json['symptoms_hi'] ?? '',
      chemicalTreatment: TreatmentInfo.fromJson(json['chemical_treatment'] ?? {}),
      organicTreatment: TreatmentInfo.fromJson(json['organic_treatment'] ?? {}),
      preventionEn: List<String>.from(json['prevention_en'] ?? []),
      preventionHi: List<String>.from(json['prevention_hi'] ?? []),
    );
  }
}

class PredictionItem {
  final String className;
  final double confidence;
  final DiseaseDetail? detail;

  PredictionItem({
    required this.className,
    required this.confidence,
    this.detail,
  });
}

class DiagnosisResult {
  final String imagePath;
  final PredictionItem topPrediction;
  final List<PredictionItem> top3;
  final DiseaseDetail detail;
  final DateTime timestamp;

  DiagnosisResult({
    required this.imagePath,
    required this.topPrediction,
    required this.top3,
    required this.detail,
    required this.timestamp,
  });
}
