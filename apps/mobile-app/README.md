# Mobile App - Flutter

Flutter mobile application for NBFCSUITE customer platform (iOS & Android).

## Features

- 🔐 User Authentication (Biometric + PIN)
- 💰 Loan Management
- 💳 Payment Processing
- 📄 Document Upload & View
- 🔔 Notifications & Reminders
- 📊 Dashboard & Analytics
- 📍 Offline Support (SQLite)

## Tech Stack

- **Framework:** Flutter 3.10+
- **Language:** Dart
- **State Management:** BLoC / Provider
- **Local Storage:** Hive / SQLite
- **API Client:** Dio
- **Auth:** Firebase Auth (optional) + JWT
- **Notifications:** Firebase Cloud Messaging (FCM)

## Project Structure

```
mobile-app/
├── lib/
│   ├── main.dart
│   ├── features/
│   │   ├── auth/
│   │   │   ├── bloc/
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   └── presentation/
│   │   ├── home/
│   │   ├── loans/
│   │   ├── payments/
│   │   ├── documents/
│   │   └── settings/
│   ├── core/
│   │   ├── network/          # Dio client
│   │   ├── storage/          # Local DB
│   │   ├── utils/
│   │   └── constants/
│   └── config/
├── test/
├── pubspec.yaml
├── pubspec.lock
└── README.md
```

## Setup

### Prerequisites

- Flutter 3.10+ installed
- Xcode (for iOS) or Android Studio (for Android)
- iOS: CocoaPods, Xcode 14+
- Android: Android SDK 21+

### Installation

```bash
cd C:\NBFCSUITE\apps\mobile-app

# Get dependencies
flutter pub get

# Generate build files (if needed)
flutter pub run build_runner build
```

### Development

```bash
# Run on connected device/emulator
flutter run

# Run in debug mode
flutter run -d emulator-id

# Run on specific device
flutter devices
flutter run -d <device-id>
```

### Build

```bash
# Build APK (Android)
flutter build apk

# Build IPA (iOS)
flutter build ios

# Build App Bundle (Google Play)
flutter build appbundle
```

## Pages to Implement

- [ ] Login & Registration
- [ ] Biometric Authentication
- [ ] Home Dashboard
- [ ] Loan Listing
- [ ] Loan Details
- [ ] Payment History
- [ ] Make Payment (via UPI/NEFT)
- [ ] Document Upload
- [ ] KYC Verification (Video/Photo)
- [ ] Settings & Profile
- [ ] Push Notifications
- [ ] Offline Mode

## BLoC Pattern

```dart
// Example BLoC structure
loans_bloc/
  ├── loans_bloc.dart
  ├── loans_event.dart
  └── loans_state.dart

// Usage
context.read<LoansBloc>().add(FetchLoansEvent());
```

## Networking

Using Dio with interceptors:
```dart
final dio = Dio();
dio.interceptors.add(AuthInterceptor());
dio.interceptors.add(LoggingInterceptor());
```

## Local Storage

Hive for local caching:
```dart
// User model
@HiveType(typeId: 0)
class User extends HiveObject {
  @HiveField(0)
  String id;
  // ...
}
```

## Testing

```bash
# Run unit tests
flutter test

# Run widget tests
flutter test test/widget_test.dart

# Coverage
flutter test --coverage
```

## CI/CD

GitHub Actions for automated builds:
- Run tests on PR
- Build APK/IPA on release
- Deploy to TestFlight/Google Play

## Firebase Integration (Optional)

```dart
// Authentication
await FirebaseAuth.instance.signInWithEmailAndPassword(
  email: email,
  password: password,
);

// Push Notifications
FirebaseMessaging.onMessage.listen((message) {
  // Handle notification
});
```

## Contributing

See `../../CONTRIBUTING.md`

## Resources

- [Flutter Docs](https://flutter.dev/docs)
- [BLoC Library](https://bloclibrary.dev/)
- [Dio Package](https://pub.dev/packages/dio)

---

**Last Updated:** 2026-06-26
**Status:** Skeleton scaffolded, ready for implementation
