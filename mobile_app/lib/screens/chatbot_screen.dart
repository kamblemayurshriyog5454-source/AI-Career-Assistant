import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:http/http.dart' as http;
import 'package:mobile_app/config/api_config.dart';

class ChatbotScreen extends StatefulWidget {
  const ChatbotScreen({super.key});

  @override
  State<ChatbotScreen> createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends State<ChatbotScreen> {
  final TextEditingController controller = TextEditingController();
  final ScrollController scrollController = ScrollController();

  final List<Map<String, dynamic>> messages = [];

  bool loading = false;

  @override
  void initState() {
    super.initState();

    messages.add({
      "sender": "bot",
      "text": """
# 👋 Welcome!

I am your **AI Career Assistant**.

I can help you with:

- 📄 Resume Review
- 🎯 ATS Score Tips
- 💼 Job Recommendations
- 🎤 Interview Preparation
- 📚 Learning Roadmap
- 🧠 Career Guidance
- 💻 Programming Questions

Ask me anything!
"""
    });
  }

  void scrollBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (scrollController.hasClients) {
        scrollController.animateTo(
          scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> sendMessage() async {
    if (controller.text.trim().isEmpty) return;

    final question = controller.text.trim();

    setState(() {
      messages.add({
        "sender": "user",
        "text": question,
      });

      loading = true;
    });

    controller.clear();
    scrollBottom();

    try {
      final response = await http.post(
        Uri.parse("${ApiConfig.baseUrl}/chat"),
        headers: {
          "Content-Type": "application/json",
        },
        body: jsonEncode({
          "question": question,
        }),
      );

      final data = jsonDecode(response.body);

      setState(() {
        loading = false;

        messages.add({
          "sender": "bot",
          "text": data["success"] == true
              ? data["answer"]
              : data["error"],
        });
      });

      scrollBottom();
    } catch (e) {
      setState(() {
        loading = false;

        messages.add({
          "sender": "bot",
          "text": e.toString(),
        });
      });

      scrollBottom();
    }
  }

  Widget buildBubble(Map<String, dynamic> msg) {
    final isUser = msg["sender"] == "user";

    return Align(
      alignment:
          isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.all(14),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: isUser ? Colors.blue : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(18),
        ),
        child: isUser
            ? Text(
                msg["text"],
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                ),
              )
            : MarkdownBody(
                data: msg["text"],
                selectable: true,
              ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("AI Career Chatbot"),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: scrollController,
              padding: const EdgeInsets.all(12),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                return buildBubble(messages[index]);
              },
            ),
          ),
          if (loading)
            const Padding(
              padding: EdgeInsets.all(10),
              child: CircularProgressIndicator(),
            ),
          const Divider(),
          Padding(
            padding: const EdgeInsets.all(10),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: controller,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => sendMessage(),
                    decoration: InputDecoration(
                      hintText: "Ask your career question...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                CircleAvatar(
                  backgroundColor: Colors.blue,
                  child: IconButton(
                    onPressed: sendMessage,
                    icon: const Icon(
                      Icons.send,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}