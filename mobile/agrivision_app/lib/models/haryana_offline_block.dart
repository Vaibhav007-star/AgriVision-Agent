/// Model representing an administrative block in Haryana with micro-regional agronomy,
/// authentic linguistic dialect, primary crops, offline symptom checklist, and CCS HAU approved solutions.
class HaryanaOfflineBlock {
  final String districtName;
  final String blockName;
  final String primaryDialect;
  final List<String> primaryCrops;
  final List<String> top3Diseases;
  final Map<String, String> symptomChecklist;
  final Map<String, String> approvedPesticideSolutions;

  HaryanaOfflineBlock({
    required this.districtName,
    required this.blockName,
    required this.primaryDialect,
    required this.primaryCrops,
    required this.top3Diseases,
    required this.symptomChecklist,
    required this.approvedPesticideSolutions,
  });

  factory HaryanaOfflineBlock.fromJson(Map<String, dynamic> json) {
    return HaryanaOfflineBlock(
      districtName: json['District_Name'] as String? ?? '',
      blockName: json['Block_Name'] as String? ?? '',
      primaryDialect: json['Primary_Dialect'] as String? ?? '',
      primaryCrops: (json['Primary_Crops'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      top3Diseases: (json['Top_3_Diseases'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      symptomChecklist: (json['Symptom_Checklist_Offline'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v.toString())) ??
          {},
      approvedPesticideSolutions:
          (json['Approved_Pesticide_Solution'] as Map<String, dynamic>?)
                  ?.map((k, v) => MapEntry(k, v.toString())) ??
              {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'District_Name': districtName,
      'Block_Name': blockName,
      'Primary_Dialect': primaryDialect,
      'Primary_Crops': primaryCrops,
      'Top_3_Diseases': top3Diseases,
      'Symptom_Checklist_Offline': symptomChecklist,
      'Approved_Pesticide_Solution': approvedPesticideSolutions,
    };
  }

  /// Extracts the simple vernacular Hindi/local name for a crop (e.g., "Sarson", "Dhan", "Gehu").
  List<String> get vernacularCropNames {
    return primaryCrops.map((c) {
      if (c.contains('(')) {
        return c.split('(')[0].trim();
      }
      if (c.contains('/')) {
        return c.split('/')[0].trim();
      }
      return c;
    }).toList();
  }
}

