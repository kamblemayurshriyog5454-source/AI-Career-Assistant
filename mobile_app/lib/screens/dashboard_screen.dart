import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'resume_builder_screen.dart';
import 'login_screen.dart';
import 'upload_resume_screen.dart';
import 'chatbot_screen.dart';
import 'package:mobile_app/config/api_config.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final FirebaseAuth auth = FirebaseAuth.instance;
  final FirebaseFirestore firestore = FirebaseFirestore.instance;

  String name = "";
  String email = "";
  String mobile = "";

  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadUserData();
  }

  Future<void> loadUserData() async {
    try {
      User? user = auth.currentUser;

      if (user == null) return;

      final snapshot =
          await firestore.collection("Users").doc(user.uid).get();

      if (snapshot.exists) {
        final data = snapshot.data();

        setState(() {
          name = data?["name"] ?? "User";
          email = data?["email"] ?? "";
          mobile = data?["mobile"] ?? "";
          isLoading = false;
        });
      } else {
        setState(() {
          name = "User";
          email = user.email ?? "";
          mobile = "";
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("AI Career Assistant"),
        centerTitle: true,
      ),
      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  const SizedBox(height: 20),

                  const CircleAvatar(
                    radius: 45,
                    backgroundColor: Colors.blue,
                    child: Icon(
                      Icons.person,
                      color: Colors.white,
                      size: 50,
                    ),
                  ),

                  const SizedBox(height: 20),

                  Text(
                    "Welcome, $name",
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  const SizedBox(height: 10),

                  Text(
                    email,
                    style: const TextStyle(fontSize: 18),
                  ),

                  const SizedBox(height: 5),

                  Text(
                    mobile,
                    style: const TextStyle(fontSize: 18),
                  ),

                  const SizedBox(height: 30),

                  buildCard(
                    Icons.upload_file,
                    "Upload Resume",
                    () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const UploadResumeScreen(),
                        ),
                      );
                    },
                  ),

                  buildCard(
                    Icons.analytics,
                    "Resume Analysis",
                    () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const UploadResumeScreen(),
                        ),
                      );
                    },
                  ),

                  buildCard(
                    Icons.score,
                    "ATS Score",
                    () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const UploadResumeScreen(),
                        ),
                      );
                    },
                  ),

                  buildCard(
                    Icons.work,
                    "Job Recommendation",
                    () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const UploadResumeScreen(),
                        ),
                      );
                    },
                  ),

                  buildCard(
                    Icons.record_voice_over,
                    "Mock Interview",
                    () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const UploadResumeScreen(),
                        ),
                      );
                    },
                  ),

                  buildCard(
                    Icons.psychology,
                    "Skill Gap Analysis",
                    () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const UploadResumeScreen(),
                        ),
                      );
                    },
                  ),

                  buildCard(
                    Icons.smart_toy,
                    "AI Career Chatbot",
                    () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const ChatbotScreen(),
                        ),
                      );
                    },
                  ),
                  buildCard(
  Icons.description,
  "Resume Builder",
  () {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const ResumeBuilderScreen(),
      ),
    );
  },
),
                  const SizedBox(height: 30),

                  SizedBox(
                    width: double.infinity,
                    height: 55,
                    child: ElevatedButton.icon(
                      icon: const Icon(Icons.logout),
                      label: const Text("Logout"),
                      onPressed: () async {
                        await auth.signOut();

                        if (!mounted) return;

                        Navigator.pushAndRemoveUntil(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const LoginScreen(),
                          ),
                          (route) => false,
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget buildCard(
    IconData icon,
    String title,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 5,
      margin: const EdgeInsets.only(bottom: 15),
      child: ListTile(
        leading: Icon(
          icon,
          color: Colors.blue,
          size: 34,
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        trailing: const Icon(Icons.arrow_forward_ios),
        onTap: onTap,
      ),
    );
  }
}