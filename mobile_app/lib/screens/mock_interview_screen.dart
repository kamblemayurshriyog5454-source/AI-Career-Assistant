import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart' as stt;

import 'package:mobile_app/config/api_config.dart';

class MockInterviewScreen extends StatefulWidget {
  final Uint8List pdfBytes;
  final String fileName;

  const MockInterviewScreen({
    super.key,
    required this.pdfBytes,
    required this.fileName,
  });

  @override
  State<MockInterviewScreen> createState() =>
      _MockInterviewScreenState();
}

class _MockInterviewScreenState
    extends State<MockInterviewScreen> {

  final FlutterTts flutterTts = FlutterTts();
  final stt.SpeechToText speech = stt.SpeechToText();

  final TextEditingController answerController =
      TextEditingController();

  bool loading = true;
  bool isListening = false;
  bool isEvaluating = false;
  bool speechAvailable = false;

  int currentQuestion = 0;

  List<String> questionList = [];
  List<String> userAnswers = [];

  String currentAnswer = "";
  String evaluation = "";

  @override
  void initState() {
    super.initState();

    initVoice();
    getQuestions();
  }

  @override
  void dispose() {
    flutterTts.stop();
    speech.stop();
    answerController.dispose();
    super.dispose();
  }

  Future<void> initVoice() async {
    try {
      await flutterTts.setLanguage("en-US");
      await flutterTts.setSpeechRate(0.45);
      await flutterTts.setPitch(1.0);
      await flutterTts.awaitSpeakCompletion(true);

      speechAvailable = await speech.initialize(
        onStatus: (status) {
          debugPrint("STATUS: $status");

          if (status == "done" ||
              status == "notListening") {
            setState(() {
              isListening = false;
            });
          }
        },
        onError: (error) {
          debugPrint(error.errorMsg);

          setState(() {
            isListening = false;
          });
        },
      );

      debugPrint(
          "Speech Available: $speechAvailable");
    } catch (e) {
      debugPrint(e.toString());

      speechAvailable = false;
    }
  }

  Future<void> speakCurrentQuestion() async {
    if (questionList.isEmpty) return;

    await flutterTts.stop();

    await flutterTts.speak(
      questionList[currentQuestion],
    );

    if (!kIsWeb && speechAvailable) {
      await Future.delayed(
        const Duration(seconds: 1),
      );

      await startListening();
    }
  }
Future<void> getQuestions() async {
  setState(() {
    loading = true;
  });

  try {
    final request = http.MultipartRequest(
      "POST",
      Uri.parse("${ApiConfig.baseUrl}/mock-interview"),
    );

    request.files.add(
      http.MultipartFile.fromBytes(
        "file",
        widget.pdfBytes,
        filename: widget.fileName,
      ),
    );

    final response = await request
        .send()
        .timeout(const Duration(seconds: 30));

    final body = await response.stream.bytesToString();

    debugPrint(body);

    if (response.statusCode != 200) {
      throw Exception(
        "Server Error (${response.statusCode})",
      );
    }

    final data = jsonDecode(body);

    if (data["success"] == true) {
      questionList =
          List<String>.from(data["questions"]);

      userAnswers =
          List.filled(questionList.length, "");

      currentQuestion = 0;

      answerController.clear();

      setState(() {
        loading = false;
      });

      await speakCurrentQuestion();
    } else {
      throw Exception(data["error"]);
    }
  } on TimeoutException {
    setState(() {
      loading = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Request Timed Out"),
      ),
    );
  } catch (e) {
    setState(() {
      loading = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(e.toString()),
      ),
    );
  }
}

Future<void> startListening() async {
  if (!speechAvailable) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          "Speech Recognition is not available.\nYou can type your answer.",
        ),
      ),
    );
    return;
  }

  if (isListening) return;

  setState(() {
    isListening = true;
  });

  await speech.listen(
    listenFor: const Duration(minutes: 2),
    pauseFor: const Duration(seconds: 5),
    partialResults: true,
    localeId: "en_US",
    cancelOnError: true,
    onResult: (result) {
      currentAnswer = result.recognizedWords;

      answerController.text = currentAnswer;

      answerController.selection =
          TextSelection.fromPosition(
        TextPosition(
          offset: answerController.text.length,
        ),
      );

      setState(() {});
    },
  );
}

Future<void> stopListening() async {
  await speech.stop();

  setState(() {
    isListening = false;
  });
}

Future<void> evaluateAnswer() async {
  if (answerController.text.trim().isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Please enter your answer."),
      ),
    );
    return;
  }

  setState(() {
    isEvaluating = true;
  });

  try {
    userAnswers[currentQuestion] =
        answerController.text;

    final response = await http
        .post(
          Uri.parse(
            "${ApiConfig.baseUrl}/evaluate-answer",
          ),
          headers: {
            "Content-Type": "application/json",
          },
          body: jsonEncode({
            "question":
                questionList[currentQuestion],
            "answer": answerController.text,
          }),
        )
        .timeout(const Duration(seconds: 30));

    final data = jsonDecode(response.body);

    if (data["success"] == true) {
      setState(() {
        evaluation = data["evaluation"];
      });
    } else {
      throw Exception(data["error"]);
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(e.toString()),
      ),
    );
  }

  setState(() {
    isEvaluating = false;
  });
}

void nextQuestion() {
  if (currentQuestion == questionList.length - 1) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Interview Completed"),
      ),
    );
    return;
  }

  userAnswers[currentQuestion] =
      answerController.text;

  setState(() {
    currentQuestion++;

    answerController.text =
        userAnswers[currentQuestion];

    evaluation = "";
  });

  speakCurrentQuestion();
}

void previousQuestion() {
  if (currentQuestion == 0) return;

  userAnswers[currentQuestion] =
      answerController.text;

  setState(() {
    currentQuestion--;

    answerController.text =
        userAnswers[currentQuestion];

    evaluation = "";
  });

  speakCurrentQuestion();
}
@override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: const Text("AI Mock Interview"),
      centerTitle: true,
      actions: [
        IconButton(
          icon: const Icon(Icons.volume_up),
          onPressed: loading ? null : speakCurrentQuestion,
        ),
      ],
    ),
    body: loading
        ? const Center(
            child: CircularProgressIndicator(),
          )
        : Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [

                // Progress
                LinearProgressIndicator(
                  value: (currentQuestion + 1) /
                      questionList.length,
                ),

                const SizedBox(height: 10),

                Text(
                  "Question ${currentQuestion + 1} of ${questionList.length}",
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 20),

                Card(
                  elevation: 5,
                  shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(15),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      questionList[currentQuestion],
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 20),

                TextField(
                  controller: answerController,
                  minLines: 5,
                  maxLines: 8,
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    labelText: "Your Answer",
                    hintText:
                        "Type your answer or use the microphone...",
                  ),
                  onChanged: (value) {
                    currentAnswer = value;
                  },
                ),

                const SizedBox(height: 15),

                Row(
                  children: [

                    Expanded(
                      child: ElevatedButton.icon(
                        icon: Icon(
                          isListening
                              ? Icons.stop
                              : Icons.mic,
                        ),
                        label: Text(
                          isListening
                              ? "Stop"
                              : "Speak",
                        ),
                        onPressed: () {
                          if (isListening) {
                            stopListening();
                          } else {
                            startListening();
                          }
                        },
                      ),
                    ),

                    const SizedBox(width: 10),

                    Expanded(
                      child: ElevatedButton.icon(
                        icon: isEvaluating
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child:
                                    CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.psychology),
                        label: Text(
                          isEvaluating
                              ? "Evaluating..."
                              : "Evaluate",
                        ),
                        onPressed: isEvaluating
                            ? null
                            : evaluateAnswer,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 20),

                if (evaluation.isNotEmpty)
                  Expanded(
                    child: Card(
                      elevation: 5,
                      shape:
                          RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(15),
                      ),
                      child: Padding(
                        padding:
                            const EdgeInsets.all(16),
                        child: SingleChildScrollView(
                          child: SelectableText(
                            evaluation,
                            style: const TextStyle(
                              fontSize: 16,
                              height: 1.5,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),

                const SizedBox(height: 15),

                Row(
                  children: [

                    Expanded(
                      child: ElevatedButton.icon(
                        icon: const Icon(
                            Icons.arrow_back),
                        label:
                            const Text("Previous"),
                        onPressed:
                            currentQuestion == 0
                                ? null
                                : previousQuestion,
                      ),
                    ),

                    const SizedBox(width: 10),

                    Expanded(
                      child: ElevatedButton.icon(
                        icon: const Icon(
                            Icons.arrow_forward),
                        label: Text(
                          currentQuestion ==
                                  questionList
                                          .length -
                                      1
                              ? "Finish"
                              : "Next",
                        ),
                        onPressed: nextQuestion,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
  );
}
}  