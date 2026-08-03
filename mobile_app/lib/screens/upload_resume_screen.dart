import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'resume_analysis_screen.dart';
class UploadResumeScreen extends StatefulWidget {
  const UploadResumeScreen({super.key});

  @override
  State<UploadResumeScreen> createState() => _UploadResumeScreenState();
}

class _UploadResumeScreenState extends State<UploadResumeScreen> {
  PlatformFile? pickedFile;

  bool uploading = false;
  double progress = 0;

  Future<void> pickResume() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      withData: kIsWeb,
    );

    if (result != null) {
      setState(() {
        pickedFile = result.files.first;
        if (pickedFile!.size > 5 * 1024 * 1024) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text("Please select a PDF smaller than 5 MB."),
      backgroundColor: Colors.red,
    ),
  );

  setState(() {
    pickedFile = null;
  });

  return;
}
      });
    }
  }

  Future<void> uploadResume() async {
    if (pickedFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Please select a PDF Resume"),
        ),
      );
      return;
    }

    try {
      setState(() {
        uploading = true;
        progress = 0;
      });

      User? user = FirebaseAuth.instance.currentUser;

      if (user == null) {
        throw Exception("User not logged in");
      }

      String uid = user.uid;

      String fileName =
          "${DateTime.now().millisecondsSinceEpoch}_${pickedFile!.name}";

      Reference ref = FirebaseStorage.instance
          .ref()
          .child("resumes")
          .child(uid)
          .child(fileName);

      UploadTask uploadTask;

      if (kIsWeb) {
        uploadTask = ref.putData(pickedFile!.bytes!);
      } else {
        uploadTask = ref.putFile(File(pickedFile!.path!));
      }

      uploadTask.snapshotEvents.listen((event) {
        if (event.totalBytes > 0) {
          setState(() {
            progress = event.bytesTransferred / event.totalBytes;
          });
        }
      });

      TaskSnapshot snapshot = await uploadTask;

      String downloadUrl = await snapshot.ref.getDownloadURL();

      DocumentSnapshot doc = await FirebaseFirestore.instance
          .collection("Users")
          .doc(uid)
          .get();

      Map<String, dynamic> oldData = {};

      if (doc.exists) {
        oldData = doc.data() as Map<String, dynamic>;
      }

      await FirebaseFirestore.instance
          .collection("Users")
          .doc(uid)
          .set({
        "name": oldData["name"] ?? "",
        "email": oldData["email"] ?? user.email,
        "mobile": oldData["mobile"] ?? "",
        "resumeName": pickedFile!.name,
        "resumeUrl": downloadUrl,
        "uploadedAt": FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
  const SnackBar(
    duration: Duration(seconds: 2),
    backgroundColor: Colors.green,
    content: Row(
      children: [
        Icon(Icons.check_circle, color: Colors.white),
        SizedBox(width: 10),
        Expanded(
          child: Text("Resume uploaded successfully.\nAnalyzing resume..."),
        ),
      ],
    ),
  ),
);

Uint8List pdfData;

if (kIsWeb) {
  pdfData = pickedFile!.bytes!;
} else {
  pdfData = await File(pickedFile!.path!).readAsBytes();
}

Navigator.push(
  context,
  MaterialPageRoute(
    builder: (_) => ResumeAnalysisScreen(
      pdfBytes: pdfData,
      fileName: pickedFile!.name,
    ),
  ),
);
    } catch (e) {
      if (!mounted) return;

      debugPrint(e.toString());

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            "Failed to upload resume.\nPlease try again.",
          ),
          backgroundColor: Colors.red,
       ),
     );
    } finally {
      if (mounted) {
        setState(() {
          uploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Upload Resume"),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const SizedBox(height: 30),
            const Icon(
              Icons.picture_as_pdf,
              size: 90,
              color: Colors.red,
            ),
            const SizedBox(height: 20),
            Card(
  elevation: 4,
  child: ListTile(
    leading: const Icon(
      Icons.picture_as_pdf,
      color: Colors.red,
    ),
    title: Text(
      pickedFile == null
          ? "No Resume Selected"
          : pickedFile!.name,
    ),
    subtitle: pickedFile == null
        ? const Text("Choose your resume in PDF format")
        : Text(
            "${(pickedFile!.size / 1024).toStringAsFixed(1)} KB",
          ),
  ),
),
            const SizedBox(height: 30),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton.icon(
                onPressed: uploading ? null : pickResume,
                icon: const Icon(Icons.folder_open),
                label: const Text("Choose Resume"),
              ),
            ),
            const SizedBox(height: 20),
            if (uploading)
              Column(
                children: [
                  ClipRRect(
                   borderRadius: BorderRadius.circular(20),
                   child: LinearProgressIndicator(
                    value: progress,
                    minHeight: 10,
                   ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    "Uploading ${(progress * 100).toStringAsFixed(0)}%",
                    style: const TextStyle(
                     fontWeight: FontWeight.bold,
                    ),
               ),
                  const SizedBox(height: 20),
                ],
              ),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton.icon(
                onPressed: uploading ? null : uploadResume,
                icon: const Icon(Icons.cloud_upload),
                label: Text(
                   uploading ? "Uploading..." : "Upload Resume",
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}