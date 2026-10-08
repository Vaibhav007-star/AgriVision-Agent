import 'dart:io';
import 'dart:convert';
import 'package:flutter/foundation.dart';
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
      debugPrint('Error initializing ClassifierService: $e');
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

    // Normalize image pixels to [-1.0, 1.0] and evaluate botanical foliage vs human skin
    final Float32List inputBuffer = Float32List(1 * 224 * 224 * 3);
    int pixelIndex = 0;
    int foliagePixels = 0;
    int skinPixels = 0;
    int centerSkinPixels = 0;
    int centerFoliagePixels = 0;
    int centerWhitePixels = 0;
    const int totalPixels = 224 * 224;
    const double centerTotalPixels = 135.0 * 135.0; // Central ~60% region (44..179)

    for (int y = 0; y < 224; y++) {
      for (int x = 0; x < 224; x++) {
        final pixel = resizedImage.getPixel(x, y);
        final num r = pixel.r;
        final num g = pixel.g;
        final num b = pixel.b;

        inputBuffer[pixelIndex++] = (r / 127.5) - 1.0;
        inputBuffer[pixelIndex++] = (g / 127.5) - 1.0;
        inputBuffer[pixelIndex++] = (b / 127.5) - 1.0;

        final bool isCenter = (x >= 44 && x <= 179 && y >= 44 && y <= 179);

        // Human skin tone check (YCbCr + RGB rules across Fitzpatrick I-VI)
        final double yVal = 0.299 * r + 0.587 * g + 0.114 * b;
        final double cr = (r - yVal) * 0.713 + 128;
        final double cb = (b - yVal) * 0.564 + 128;
        final bool isSkinPixel = (r > 70 && g > 35 && b > 20 &&
            r > g && r > b && (r - b) >= 12 && (r - g) >= 6 &&
            cr >= 132 && cr <= 182 && cb >= 75 && cb <= 135 && (cr - cb) >= 20);

        // Achromatic white (white shirts, white dog fur, paper)
        final num maxVal = [r, g, b].reduce((curr, next) => curr > next ? curr : next);
        final num minVal = [r, g, b].reduce((curr, next) => curr < next ? curr : next);
        final double satVal = maxVal == 0 ? 0.0 : (maxVal - minVal) / maxVal;
        final bool isWhiteAchromatic = (satVal < 0.18 && maxVal > 165);

        if (isSkinPixel) {
          skinPixels++;
          if (isCenter) centerSkinPixels++;
        }

        if (isWhiteAchromatic && isCenter) {
          centerWhitePixels++;
        }

        // Botanical foliage check (Strictly excluding human skin and white objects)
        final bool isFoliagePixel = !isSkinPixel && !isWhiteAchromatic && (
            (g > r * 0.92 && g > b * 1.05 && g > 30) ||
            (g > 55 && g > r * 0.90 && g > b)
        );

        if (isFoliagePixel) {
          foliagePixels++;
          if (isCenter) centerFoliagePixels++;
        }
      }
    }

    final double foliageRatio = foliagePixels / totalPixels;
    final double skinRatio = skinPixels / totalPixels;
    final double centerSkinRatio = centerSkinPixels / centerTotalPixels;
    final double centerFoliageRatio = centerFoliagePixels / centerTotalPixels;
    final double centerWhiteRatio = centerWhitePixels / centerTotalPixels;

    // Hardened guardrail rules
    final bool isHuman = (centerSkinRatio >= 0.12 && centerFoliageRatio < 0.65) ||
        (skinRatio >= 0.14) ||
        (centerSkinRatio >= 0.20);
    final bool isAnimalOrClothing = (centerWhiteRatio >= 0.12 && centerFoliageRatio < 0.75);
    final bool isLandscapeOrLawn = (centerFoliageRatio < 0.60);
    final bool isNonLeaf = isHuman || isAnimalOrClothing || isLandscapeOrLawn || foliageRatio < 0.10;

    if (isNonLeaf) {
      String reasonEn = "No crop leaf detected. Please upload a close-up photo of an authentic crop leaf.";
      String reasonHi = "छवि में पौधे के पत्तों के लक्षण नहीं मिले। कृपया पौधे की पत्ती की स्पष्ट तस्वीर लें।";

      if (isHuman) {
        reasonEn = "Human subject detected. AgriVision is strictly designed for crop leaf pathology, not human medical diagnostics.";
        reasonHi = "मानव त्वचा या चेहरा पहचाना गया। यह ऐप केवल फसल की पत्तियों के रोग निदान के लिए है।";
      } else if (isAnimalOrClothing) {
        reasonEn = "Animal or synthetic clothing subject detected (dog/pet or apparel). AgriVision tests only authentic agricultural crop leaves.";
        reasonHi = "पालतू जानवर या कपड़े पहचाने गए हैं। एग्रीविज़न केवल समर्थित फसलों की पत्तियों का परीक्षण करता है।";
      } else if (isLandscapeOrLawn) {
        reasonEn = "Landscape scene or lawn turf detected. Please photograph a close-up crop leaf blade (Tomato, Potato, Pepper, etc.).";
        reasonHi = "परिदृश्य या घास का मैदान पहचाना गया। कृपया फसल की पत्ती की क्लोज-अप तस्वीर लें।";
      }

      final nonLeafDetail = DiseaseDetail(
        cropEn: "Non-Plant / OOD Subject",
        cropHi: "गैर-फसल छवि",
        diseaseEn: "No Crop Leaf Detected",
        diseaseHi: "पत्ती की पहचान नहीं हुई",
        isHealthy: false,
        severity: "Rejected",
        pathogenType: "Non-Botanical Input",
        symptomsEn: reasonEn,
        symptomsHi: reasonHi,
        chemicalTreatment: TreatmentInfo(
          nameEn: "Disabled (Do not spray chemicals on humans or non-plants)",
          nameHi: "अक्षम (मानव या गैर-पौधों पर कीटनाशक न छिड़कें)",
          dosagePerLiter: "0 g/L (No chemical treatment)",
          sprayIntervalDays: "N/A",
          phiDays: 0,
        ),
        organicTreatment: TreatmentInfo(
          nameEn: "Not Applicable",
          nameHi: "लागू नहीं",
          dosagePerLiter: "0 ml/L",
          sprayIntervalDays: "N/A",
          phiDays: 0,
        ),
        preventionEn: [
          "Photograph affected crop leaves in clear daylight.",
          "Ensure the leaf covers at least 25% of the camera view.",
          "Supported crops: Tomato, Potato, Pepper, Apple, Corn."
        ],
        preventionHi: [
          "प्राकृतिक रोशनी में पौधे की पत्ती की स्पष्ट तस्वीर लें।",
          "सुनिश्चित करें कि पत्ती कैमरे के फ्रेम का कम से कम 25% हिस्सा कवर करे।",
          "समर्थित फसलें: टमाटर, आलू, शिमला मिर्च, सेब, मक्का।"
        ],
      );

      final topItem = PredictionItem(
        className: 'Non_Leaf',
        confidence: 0.0,
        detail: nonLeafDetail,
      );

      return DiagnosisResult(
        imagePath: imageFile.path,
        topPrediction: topItem,
        top3: [topItem],
        detail: nonLeafDetail,
        timestamp: DateTime.now(),
      );
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
