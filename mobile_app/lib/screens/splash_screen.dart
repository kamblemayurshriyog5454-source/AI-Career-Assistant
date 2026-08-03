import 'dart:async';
import 'package:flutter/material.dart';
import 'login_screen.dart';
import 'package:mobile_app/config/api_config.dart';
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {

  @override
  void initState() {
    super.initState();

    Timer(
      const Duration(seconds: 3),
      () {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => const LoginScreen(),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue,

      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,

          children: [

            Icon(
              Icons.smart_toy,
              size: 100,
              color: Colors.white,
            ),

            SizedBox(height: 20),

            Text(
              "AI Career Assistant",
              style: TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),

            SizedBox(height: 10),

            Text(
              "Your AI Career Guide",
              style: TextStyle(
                color: Colors.white70,
                fontSize: 18,
              ),
            ),

            SizedBox(height: 40),

            CircularProgressIndicator(
              color: Colors.white,
            ),

          ],
        ),
      ),
    );
  }
}