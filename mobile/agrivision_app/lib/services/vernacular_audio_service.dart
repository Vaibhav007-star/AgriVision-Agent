import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

/// Singleton service providing vernacular offline Text-to-Speech (TTS) audio playback
/// calibrated for rural Haryana dialects (Ahirwati, Bagri, Mewati, Puadhi, Bangru/Haryanvi).
class VernacularAudioService {
  static final VernacularAudioService _instance = VernacularAudioService._internal();
  factory VernacularAudioService() => _instance;
  VernacularAudioService._internal();

  final FlutterTts _tts = FlutterTts();
  bool _isInitialized = false;
  bool _isPlaying = false;

  bool get isPlaying => _isPlaying;

  Future<void> initialize() async {
    if (_isInitialized) return;
    try {
      await _tts.awaitSpeakCompletion(true);
      await _tts.setPitch(1.0);
      await _tts.setSpeechRate(0.85); // Slightly slower rate for rural acoustic clarity

      _tts.setStartHandler(() {
        _isPlaying = true;
      });

      _tts.setCompletionHandler(() {
        _isPlaying = false;
      });

      _tts.setCancelHandler(() {
        _isPlaying = false;
      });

      _tts.setErrorHandler((msg) {
        _isPlaying = false;
        debugPrint('VernacularAudioService TTS Error: $msg');
      });

      _isInitialized = true;
    } catch (e) {
      debugPrint('VernacularAudioService initialize error: $e');
    }
  }

  /// Speaks the complete prescription and dosage instructions.
  Future<void> speakPrescription({
    required String crop,
    required String disease,
    required String chemicalRemedy,
    required String dosage,
    bool isHindi = true,
    String? dialect,
  }) async {
    await initialize();

    String speechText;
    if (isHindi) {
      try {
        await _tts.setLanguage('hi-IN');
      } catch (_) {}

      final String dialectGreeting = _getDialectSalutation(dialect);
      speechText = '$dialectGreeting। आपकी $crop फसल में $disease का प्रकोप पहचाना गया है। '
          'हरियाणा कृषि विश्वविद्यालय की संस्तुति के अनुसार: $chemicalRemedy का छिड़काव करें। '
          'खुराक: $dosage। छिड़काव हमेशा शांत मौसम में करें।';
    } else {
      try {
        await _tts.setLanguage('en-IN');
      } catch (_) {}

      speechText = 'Agronomic Advisory for $crop. Detected pathogen is $disease. '
          'Recommended treatment: Apply $chemicalRemedy. Dosage: $dosage. '
          'Spray during calm morning hours.';
    }

    try {
      _isPlaying = true;
      await _tts.stop();
      await _tts.speak(speechText);
    } catch (e) {
      _isPlaying = false;
      debugPrint('VernacularAudioService speak error: $e');
    }
  }

  /// Speaks Haryana offline diagnostic chain step-by-step.
  Future<void> speakDiagnosticChain({
    required String blockName,
    required String dialect,
    required String disease,
    required String chain,
    required String solution,
    bool isHindi = true,
  }) async {
    await initialize();

    String speechText;
    if (isHindi) {
      try {
        await _tts.setLanguage('hi-IN');
      } catch (_) {}

      speechText = 'राम-राम किसान भाई। खंड $blockName, बोली $dialect के लिए $disease का निदान: '
          'लक्षण क्रम है: $chain। '
          'चौधरी चरण सिंह हरियाणा कृषि विश्वविद्यालय अनुसार अनुमोदित दवा: $solution।';
    } else {
      try {
        await _tts.setLanguage('en-IN');
      } catch (_) {}

      speechText = 'Offline Diagnostic Advisory for $blockName Block. '
          'Identified condition: $disease. '
          'Symptom chain: $chain. '
          'CCS HAU Approved Solution: $solution.';
    }

    try {
      _isPlaying = true;
      await _tts.stop();
      await _tts.speak(speechText);
    } catch (e) {
      _isPlaying = false;
      debugPrint('VernacularAudioService speak diagnostic error: $e');
    }
  }

  /// Stops any currently playing audio.
  Future<void> stop() async {
    try {
      await _tts.stop();
      _isPlaying = false;
    } catch (e) {
      debugPrint('VernacularAudioService stop error: $e');
    }
  }

  /// Regional salutation generator based on micro-dialect.
  String _getDialectSalutation(String? dialect) {
    if (dialect == null) return 'राम-राम किसान भाई';
    final d = dialect.toLowerCase();
    if (d.contains('ahir')) {
      return 'राम-राम जी, अहिरवाटी अंचल के किसान भाई';
    } else if (d.contains('bagri')) {
      return 'खम्मा घणी, बागड़ी क्षेत्र के किसान भाई';
    } else if (d.contains('mewati')) {
      return 'सलाम वालेकुम, मेवात क्षेत्र के किसान भाई';
    } else if (d.contains('puadhi')) {
      return 'सत श्री अकाल, पुआधी बेल्ट के किसान भाई';
    } else {
      return 'राम-राम किसान भाई';
    }
  }

  void dispose() {
    _tts.stop();
  }
}

