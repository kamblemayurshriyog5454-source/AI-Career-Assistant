import 'dart:io';
import 'package:flutter/foundation.dart';

class ApiConfig {
  static String get baseUrl {
    // Chrome / Edge (Flutter Web)
    if (kIsWeb) {
      return "http://127.0.0.1:8000";
    }

    // Real Android Phone
    if (Platform.isAndroid) {
      return "http://172.20.10.5:8000";
    }

    // iPhone (if you use one later)
    if (Platform.isIOS) {
      return "http://172.20.10.5:8000";
    }

    // Windows / macOS / Linux
    return "http://127.0.0.1:8000";
  }
}