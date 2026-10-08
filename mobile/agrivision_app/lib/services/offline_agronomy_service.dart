import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import '../models/haryana_offline_block.dart';

/// Singleton service providing 100% offline access to the micro-regional agronomy,
/// indigenous dialects, symptom checklists, and CCS HAU approved solutions across Haryana.
class OfflineAgronomyService {
  static final OfflineAgronomyService _instance = OfflineAgronomyService._internal();
  factory OfflineAgronomyService() => _instance;
  OfflineAgronomyService._internal();

  List<HaryanaOfflineBlock> _blocks = [];
  bool _isLoaded = false;

  bool get isLoaded => _isLoaded;
  List<HaryanaOfflineBlock> get blocks => _blocks;

  /// Loads and parses the embedded offline JSON asset.
  Future<void> initialize() async {
    if (_isLoaded) return;
    try {
      final String jsonString = await rootBundle.loadString('assets/haryana_offline_blocks.json');
      final List<dynamic> jsonList = json.decode(jsonString) as List<dynamic>;
      _blocks = jsonList
          .map((item) => HaryanaOfflineBlock.fromJson(item as Map<String, dynamic>))
          .toList();
      _isLoaded = true;
    } catch (e) {
      // Graceful fallback if asset loading is interrupted
      _isLoaded = false;
      rethrow;
    }
  }

  /// Returns sorted unique list of all 22 Haryana districts.
  List<String> getDistricts() {
    final districts = _blocks.map((b) => b.districtName).toSet().toList();
    districts.sort();
    return districts;
  }

  /// Returns all administrative blocks under a given district.
  List<HaryanaOfflineBlock> getBlocksForDistrict(String districtName) {
    final clean = districtName.trim().toLowerCase();
    return _blocks.where((b) => b.districtName.toLowerCase() == clean).toList();
  }

  /// Returns specific block in a district.
  HaryanaOfflineBlock? getBlock(String districtName, String blockName) {
    final cleanDist = districtName.trim().toLowerCase();
    final cleanBlock = blockName.trim().toLowerCase();
    for (final b in _blocks) {
      if (b.districtName.toLowerCase() == cleanDist &&
          (b.blockName.toLowerCase() == cleanBlock || b.blockName.toLowerCase().contains(cleanBlock))) {
        return b;
      }
    }
    return null;
  }

  /// Returns unique list of cultural dialects across Haryana.
  List<String> getDialects() {
    final dialects = _blocks.map((b) => b.primaryDialect).toSet().toList();
    dialects.sort();
    return dialects;
  }

  /// Filters blocks by cultural dialect (Ahirwati, Bagri, Bangru, Puadhi, Mewati, Braj, Deshwali).
  List<HaryanaOfflineBlock> getBlocksByDialect(String dialectQuery) {
    final clean = dialectQuery.trim().toLowerCase();
    return _blocks.where((b) => b.primaryDialect.toLowerCase().contains(clean)).toList();
  }

  /// Searches blocks cultivating a specific crop (supports vernacular e.g. "Sarson", "Gwar", "Dhan").
  List<HaryanaOfflineBlock> searchByCrop(String cropQuery) {
    final clean = cropQuery.trim().toLowerCase();
    return _blocks.where((b) => b.primaryCrops.any((c) => c.toLowerCase().contains(clean))).toList();
  }

  /// Returns diagnostic symptom chains for a specific block.
  Map<String, String> getDiagnosticChains(String districtName, String blockName) {
    final block = getBlock(districtName, blockName);
    return block?.symptomChecklist ?? {};
  }

  /// Returns CCS HAU Hisar approved pesticide solutions for a specific block.
  Map<String, String> getPesticideSolutions(String districtName, String blockName) {
    final block = getBlock(districtName, blockName);
    return block?.approvedPesticideSolutions ?? {};
  }
}
