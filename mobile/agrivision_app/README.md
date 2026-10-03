# 🌿 AgriVision Mobile (Flutter + TFLite)
### 100% Free • Fully Offline On-Device AI • Zero Server Latency

AgriVision Mobile is a standalone native smartphone application for Indian farmers and agronomists. It runs our trained MobileNetV2 Deep Learning model directly on the smartphone CPU/NPU using TensorFlow Lite without requiring internet access or cloud servers.

---

## 🚀 Key Capabilities

1. **⚡ 100% Offline AI Diagnosis**:
   - Analyzes leaf photos in milliseconds directly on the phone.
   - 2.77 MB quantized TensorFlow Lite (`.tflite`) model bundled inside the APK.
2. **🎯 15 Crop Disease Classes**:
   - **Tomato**: Early Blight, Late Blight, Bacterial Spot, Septoria Leaf Spot, Leaf Mold, Spider Mites, Target Spot, Tomato Mosaic Virus, Yellow Leaf Curl Virus, Healthy.
   - **Potato**: Early Blight, Late Blight, Healthy.
   - **Bell Pepper**: Bacterial Spot, Healthy.
3. **🌐 Bilingual Support**:
   - Instant 1-tap toggle between **English** and **हिन्दी (Hindi)**.
4. **🧪 Smart Tank & Dosage Calculator**:
   - Dynamic field acreage slider (0.5 to 10 acres / bigha).
   - Computes water volume in Liters, exact chemical grams/kg, organic bio-spray milliliters, and number of 15-Liter knapsack backpack sprayer pumps needed.
5. **🛡️ Farmer Safety & Best Practices**:
   - Pre-Harvest Interval (PHI) waiting periods and mandatory PPE protective equipment guidance.

---

## 📁 Project Structure

```text
mobile/agrivision_app/
├── assets/
│   ├── crop_disease_model.tflite    # 2.77 MB optimized TFLite model
│   ├── labels.txt                   # 15 class label registry
│   └── disease_database.json        # Bilingual agronomy & treatment knowledge
├── lib/
│   ├── main.dart                    # App entry point, Emerald Green Material 3 theme
│   ├── models/
│   │   └── disease_info.dart        # Data classes for diagnosis and treatments
│   ├── services/
│   │   ├── classifier_service.dart  # tflite_flutter image preprocessing & inference
│   │   └── dosage_service.dart      # Offline mathematical dosage & tank engine
│   └── screens/
│       ├── home_screen.dart         # Camera / Gallery leaf scanner UI
│       ├── result_screen.dart       # Diagnosis results, Top-3 ranking, tabs
│       └── dosage_calculator_screen.dart # Standalone field dosage calculator
└── pubspec.yaml                     # Dependencies & asset declarations
```

---

## 🛠️ Step-by-Step Setup Guide ($0 Cost)

### Step 1: Install Flutter SDK (Free)
1. Download Flutter SDK from the official website:
   👉 [https://docs.flutter.dev/get-started/install/windows/mobile](https://docs.flutter.dev/get-started/install/windows/mobile)
2. Extract the zip (e.g. to `C:\flutter`).
3. Add `C:\flutter\bin` to your Windows Environment Variables `PATH`.
4. Open a new PowerShell terminal and verify:
   ```powershell
   flutter doctor
   ```

### Step 2: Install Android Studio (Free)
1. Download Android Studio from:
   👉 [https://developer.android.com/studio](https://developer.android.com/studio)
2. During setup, check **Android SDK Platform-Tools** and **Android SDK Command-line Tools**.
3. Accept the Android licenses:
   ```powershell
   flutter doctor --android-licenses
   ```

### Step 3: Run the App on Your Phone (Debug Mode)
1. Enable **Developer Options** and **USB Debugging** on your Android smartphone.
2. Connect your phone via USB cable to your PC.
3. In PowerShell, navigate to the mobile app folder:
   ```powershell
   cd "c:\Projects\AgriVision Agent\mobile\agrivision_app"
   flutter pub get
   flutter run
   ```
   *The app will launch directly onto your phone screen!*

---

## 📦 Building the Standalone Offline APK File

To generate an installable `.apk` file that can be copied to any Android device or sent over WhatsApp / Bluetooth:

```powershell
cd "c:\Projects\AgriVision Agent\mobile\agrivision_app"
flutter build apk --release
```

The compiled APK will be ready at:
```text
mobile/agrivision_app/build/app/outputs/flutter-apk/app-release.apk
```

**Size**: ~15-20 MB complete with AI model, icons, database, and offline runtime!
You can install this APK on any farmer's phone, turn on Airplane mode (no internet), and test leaf scanning instantly!
