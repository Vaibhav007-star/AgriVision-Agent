import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';
import '../models/disease_info.dart';

class ClassifierService {
  Interpreter? _interpreter;
  List<String> _labels = [];
  Map<String, dynamic> _database = {};
  bool _isInitialized = false;

  bool get isInitialized => _isInitialized;

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // 1. Load TFLite Model from assets
      final options = InterpreterOptions()..threads = 4;
      _interpreter = await Interpreter.fromAsset(
        'assets/crop_disease_model.tflite',
        options: options,
      );

      // 2. Load Labels
      final labelsData = await rootBundle.loadString('assets/labels.txt');
      _labels = labelsData
          .split('\n')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList();

      // 3. Load Disease Knowledgebase JSON
      final jsonString = await rootBundle.loadString('assets/disease_database.json');
      _database = json.decode(jsonString);

      _isInitialized = true;
    } catch (e) {
      print('Error initializing ClassifierService: $e');
      rethrow;
    }
  }

  Future<DiagnosisResult> classifyImage(File imageFile) async {
    if (!_isInitialized || _interpreter == null) {
      await initialize();
    }

    // Read image bytes and decode
    final Uint8List imageBytes = await imageFile.readAsBytes();
    final img.Image? decodedImage = img.decodeImage(imageBytes);

    if (decodedImage == null) {
      throw Exception("Unable to decode leaf image.");
    }

    // Resize image to 224x224 (required input shape for MobileNetV2)
    final img.Image resizedImage = img.copyResize(
      decodedImage,
      width: 224,
      height: 224,
    );

    // Normalize image pixels to [-1.0, 1.0]
    // Matches training preprocessing: (pixel / 127.5) - 1.0
    final Float32List inputBuffer = Float32List(1 * 224 * 224 * 3);
    int pixelIndex = 0;

    for (int y = 0; y < 224; y++) {
      for (int x = 0; x < 224; x++) {
        final pixel = resizedImage.getPixel(x, y);
        inputBuffer[pixelIndex++] = (pixel.r / 127.5) - 1.0;
        inputBuffer[pixelIndex++] = (pixel.g / 127.5) - 1.0;
        inputBuffer[pixelIndex++] = (pixel.b / 127.5) - 1.0;
      }
    }

    // Reshape input tensor: [1, 224, 224, 3]
    final input = inputBuffer.reshape([1, 224, 224, 3]);

    // Prepare output tensor: [1, 15]
    final numClasses = _labels.isNotEmpty ? _labels.length : 15;
    final output = List.filled(1 * numClasses, 0.0).reshape([1, numClasses]);

    // Execute on-device neural network inference
    _interpreter!.run(input, output);

    final List<double> probabilities = List<double>.from(output[0]);

    // Rank predictions by confidence
    final List<MapEntry<int, double>> ranked = [];
    for (int i = 0; i < probabilities.length; i++) {
      ranked.add(MapEntry(i, probabilities[i]));
    }
    ranked.sort((a, b) => b.value.compareTo(a.value));

    // Map top 3 predictions
    final List<PredictionItem> top3 = [];
    for (int i = 0; i < 3 && i < ranked.length; i++) {
      final index = ranked[i].key;
      final conf = ranked[i].value;
      final name = index < _labels.length ? _labels[index] : 'Class_$index';
      final detail = _getDetailForClass(name);
      top3.add(PredictionItem(className: name, confidence: conf, detail: detail));
    }

    final topPrediction = top3.first;
    final primaryDetail = topPrediction.detail ?? _getDefaultDetail(topPrediction.className);

    return DiagnosisResult(
      imagePath: imageFile.path,
      topPrediction: topPrediction,
      top3: top3,
      detail: primaryDetail,
      timestamp: DateTime.now(),
    );
  }

  DiseaseDetail? _getDetailForClass(String className) {
    if (_database.containsKey(className)) {
      return DiseaseDetail.fromJson(_database[className]);
    }
    return null;
  }

  DiseaseDetail _getDefaultDetail(String className) {
    return DiseaseDetail(
      cropEn: "Plant",
      cropHi: "फसल",
      diseaseEn: className.replaceAll('_', ' '),
      diseaseHi: className.replaceAll('_', ' '),
      isHealthy: className.toLowerCase().contains("healthy"),
      severity: "Moderate",
      pathogenType: "Agricultural Condition",
      symptomsEn: "Visual symptoms identified from leaf patterns.",
      symptomsHi: "पत्तियों के लक्षणों के आधार पर पहचान की गई।",
      chemicalTreatment: TreatmentInfo(
        nameEn: "Broad Spectrum Protectant Fungicide (Mancozeb 75% WP)",
        nameHi: "व्यापक सुरक्षात्मक फफूंदनाशक (मैंकोजेब)",
        dosagePerLiter: "2.5 g per Liter",
        sprayIntervalDays: "7 to 10 days",
        phiDays: 7,
      ),
      organicTreatment: TreatmentInfo(
        nameEn: "Neem Oil 10,000 ppm + Trichoderma bio-agent",
        nameHi: "नीम का तेल + ट्राइकोडर्मा जैविक कल्चर",
        dosagePerLiter: "5 ml Neem Oil per Liter",
        sprayIntervalDays: "7 days",
        phiDays: 0,
      ),
      preventionEn: [
        "Avoid overhead irrigation.",
        "Remove diseased leaf debris from field."
      ],
      preventionHi: [
        "ऊपर से फव्वारा सिंचाई न करें।",
        "खेत से संक्रमित पत्तियां हटा दें।"
      ],
    );
  }

  void dispose() {
    _interpreter?.close();
  }
}
