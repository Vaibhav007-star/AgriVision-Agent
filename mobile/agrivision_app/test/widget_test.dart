import 'package:flutter_test/flutter_test.dart';
import 'package:agrivision_mobile/main.dart';

void main() {
  testWidgets('AgriVision app smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const AgriVisionMobileApp());
    expect(find.text('AgriVision AI'), findsOneWidget);
  });
}

