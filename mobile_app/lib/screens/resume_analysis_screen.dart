import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'package:mobile_app/config/api_config.dart';
import 'job_recommendation_screen.dart';

class ResumeAnalysisScreen extends StatefulWidget {
  final Uint8List pdfBytes;
  final String fileName;

  const ResumeAnalysisScreen({
    super.key,
    required this.pdfBytes,
    required this.fileName,
  });

  @override
  State<ResumeAnalysisScreen> createState() =>
      _ResumeAnalysisScreenState();
}

class _ResumeAnalysisScreenState
    extends State<ResumeAnalysisScreen> {

  bool loading = true;
  bool hasError = false;

  String result = "";
  String errorMessage = "";

  @override
  void initState() {
    super.initState();
    analyzeResume();
  }
Future<void> analyzeResume() async {
  setState(() {
    loading = true;
    hasError = false;
    result = "";
    errorMessage = "";
  });

  try {
    final request = http.MultipartRequest(
      "POST",
      Uri.parse("${ApiConfig.baseUrl}/analyze"),
    );

    request.files.add(
      http.MultipartFile.fromBytes(
        "file",
        widget.pdfBytes,
        filename: widget.fileName,
      ),
    );

    final streamedResponse = await request
        .send()
        .timeout(const Duration(seconds: 30));

    final responseBody =
        await streamedResponse.stream.bytesToString();

    debugPrint(
      "Resume Analysis Status: ${streamedResponse.statusCode}",
    );

    debugPrint(responseBody);

    if (streamedResponse.statusCode != 200) {
      throw Exception(
        "Server Error (${streamedResponse.statusCode})",
      );
    }

    final data = jsonDecode(responseBody);

    if (data["success"] == true) {
      setState(() {
        result = data["analysis"]?.toString() ??
            "No analysis returned.";
        loading = false;
      });
    } else {
      setState(() {
        loading = false;
        hasError = true;
        errorMessage = data["error"]?.toString() ??
            "Unknown server error.";
      });
    }
  } on TimeoutException {
    setState(() {
      loading = false;
      hasError = true;
      errorMessage =
          "The request timed out.\nPlease check your internet connection and try again.";
    });
  } on FormatException {
    setState(() {
      loading = false;
      hasError = true;
      errorMessage =
          "Invalid response received from the server.";
    });
  } catch (e) {
    debugPrint(e.toString());

    setState(() {
      loading = false;
      hasError = true;
      errorMessage =
          "Unable to connect to the backend.\n\n$e";
    });
  }
}  
Widget buildLoadingScreen() {
  return Center(
    child: Padding(
      padding: const EdgeInsets.all(25),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [

          CircularProgressIndicator(
            strokeWidth: 5,
          ),

          SizedBox(height: 25),

          Text(
            "Analyzing Resume...",
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),

          SizedBox(height: 15),

          Text(
            "Our AI is reading your resume and preparing a detailed report.",
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
              height: 1.5,
            ),
          ),

          SizedBox(height: 30),

          LinearProgressIndicator(),

          SizedBox(height: 15),

          Text(
            "This usually takes 10-20 seconds.",
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
        ],
      ),
    ),
  );
}

Widget buildErrorScreen() {
  return Center(
    child: Padding(
      padding: const EdgeInsets.all(25),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [

          const Icon(
            Icons.cloud_off,
            color: Colors.red,
            size: 90,
          ),

          const SizedBox(height: 20),

          const Text(
            "Analysis Failed",
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 15),

          Text(
            errorMessage,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 16,
              height: 1.5,
            ),
          ),

          const SizedBox(height: 30),

          SizedBox(
            width: double.infinity,
            height: 55,
            child: ElevatedButton.icon(
              onPressed: analyzeResume,
              icon: const Icon(Icons.refresh),
              label: const Text(
                "Retry Analysis",
                style: TextStyle(fontSize: 18),
              ),
            ),
          ),
        ],
      ),
    ),
  );
}
Widget buildResultScreen() {
  return SingleChildScrollView(
    padding: const EdgeInsets.all(20),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [

        Card(
          elevation: 8,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [

                Row(
                  children: const [

                    Icon(
                      Icons.analytics,
                      color: Colors.blue,
                      size: 30,
                    ),

                    SizedBox(width: 10),

                    Text(
                      "Resume Analysis Report",
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),

                const Divider(height: 30),

                SelectableText(
                  result,
                  style: const TextStyle(
                    fontSize: 17,
                    height: 1.7,
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 25),

        SizedBox(
          height: 55,
          child: ElevatedButton.icon(
            icon: const Icon(Icons.refresh),
            label: const Text(
              "Analyze Again",
              style: TextStyle(fontSize: 18),
            ),
            onPressed: analyzeResume,
          ),
        ),

        const SizedBox(height: 15),

        SizedBox(
          height: 55,
          child: ElevatedButton.icon(
            icon: const Icon(Icons.work),
            label: const Text(
              "View Job Recommendations",
              style: TextStyle(fontSize: 18),
            ),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => JobRecommendationScreen(
                    pdfBytes: widget.pdfBytes,
                    fileName: widget.fileName,
                  ),
                ),
              );
            },
          ),
        ),
      ],
    ),
  );
}
@override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      elevation: 0,
      centerTitle: true,
      title: const Text(
        "Resume Analysis",
        style: TextStyle(
          fontWeight: FontWeight.bold,
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.refresh),
          tooltip: "Analyze Again",
          onPressed: loading ? null : analyzeResume,
        ),
      ],
    ),

    body: AnimatedSwitcher(
      duration: const Duration(milliseconds: 500),
      child: loading
          ? buildLoadingScreen()
          : hasError
              ? buildErrorScreen()
              : buildResultScreen(),
    ),
  );
}
}