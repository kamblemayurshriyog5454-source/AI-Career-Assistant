import 'package:flutter/material.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:mobile_app/config/api_config.dart';
class ResumeBuilderScreen extends StatefulWidget {
  const ResumeBuilderScreen({super.key});

  @override
  State<ResumeBuilderScreen> createState() => _ResumeBuilderScreenState();
}

class _ResumeBuilderScreenState extends State<ResumeBuilderScreen> {
  final _formKey = GlobalKey<FormState>();

  final nameController = TextEditingController();
  final emailController = TextEditingController();
  final mobileController = TextEditingController();
  final addressController = TextEditingController();

  final linkedinController = TextEditingController();
  final githubController = TextEditingController();

  final objectiveController = TextEditingController();
  final educationController = TextEditingController();
  final skillsController = TextEditingController();
  final experienceController = TextEditingController();
  final projectController = TextEditingController();
  final certificationController = TextEditingController();
  final achievementController = TextEditingController();

  Widget buildField(
    String label,
    TextEditingController controller, {
    int maxLines = 1,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 15),
      child: TextFormField(
        controller: controller,
        maxLines: maxLines,
        validator: (value) {
          if (value == null || value.isEmpty) {
            return "Enter $label";
          }
          return null;
        },
        decoration: InputDecoration(
          labelText: label,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  Future<void> generateResumePDF() async {
        final pdf = pw.Document();

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(30),

        build: (context) => [

          pw.Center(
            child: pw.Text(
              nameController.text,
              style: pw.TextStyle(
                fontSize: 28,
                fontWeight: pw.FontWeight.bold,
              ),
            ),
          ),

          pw.SizedBox(height: 8),

          pw.Center(
            child: pw.Text(
              "${emailController.text} | ${mobileController.text}",
            ),
          ),

          pw.Center(
            child: pw.Text(addressController.text),
          ),

          pw.SizedBox(height: 15),

          pw.Divider(),

          pw.Text(
            "Career Objective",
            style: pw.TextStyle(
              fontSize: 18,
              fontWeight: pw.FontWeight.bold,
            ),
          ),

          pw.Text(objectiveController.text),

          pw.SizedBox(height: 10),

          pw.Text(
            "Education",
            style: pw.TextStyle(
              fontSize: 18,
              fontWeight: pw.FontWeight.bold,
            ),
          ),

          pw.Text(educationController.text),

          pw.SizedBox(height: 10),

          pw.Text(
            "Skills",
            style: pw.TextStyle(
              fontSize: 18,
              fontWeight: pw.FontWeight.bold,
            ),
          ),

          pw.Text(skillsController.text),

          pw.SizedBox(height: 10),

          pw.Text(
            "Experience",
            style: pw.TextStyle(
              fontSize: 18,
              fontWeight: pw.FontWeight.bold,
            ),
          ),

          pw.Text(experienceController.text),

          pw.SizedBox(height: 10),

          pw.Text(
            "Projects",
            style: pw.TextStyle(
              fontSize: 18,
              fontWeight: pw.FontWeight.bold,
            ),
          ),

          pw.Text(projectController.text),

          pw.SizedBox(height: 10),

          pw.Text(
            "Certifications",
            style: pw.TextStyle(
              fontSize: 18,
              fontWeight: pw.FontWeight.bold,
            ),
          ),

          pw.Text(certificationController.text),

          pw.SizedBox(height: 10),

          pw.Text(
            "Achievements",
            style: pw.TextStyle(
              fontSize: 18,
              fontWeight: pw.FontWeight.bold,
            ),
          ),

          pw.Text(achievementController.text),
        ],
      ),
    );

    await Printing.layoutPdf(
      onLayout: (format) async => pdf.save(),
    );
  }
    @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Resume Builder"),
        centerTitle: true,
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [

              buildField("Full Name", nameController),

              buildField("Email", emailController),

              buildField("Mobile Number", mobileController),

              buildField("Address", addressController),

              buildField("LinkedIn URL", linkedinController),

              buildField("GitHub URL", githubController),

              buildField(
                "Career Objective",
                objectiveController,
                maxLines: 4,
              ),

              buildField(
                "Education",
                educationController,
                maxLines: 4,
              ),

              buildField(
                "Skills",
                skillsController,
                maxLines: 4,
              ),

              buildField(
                "Experience",
                experienceController,
                maxLines: 5,
              ),

              buildField(
                "Projects",
                projectController,
                maxLines: 5,
              ),

              buildField(
                "Certifications",
                certificationController,
                maxLines: 4,
              ),

              buildField(
                "Achievements",
                achievementController,
                maxLines: 4,
              ),

              const SizedBox(height: 30),

              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.picture_as_pdf),
                  label: const Text(
                    "Generate Resume",
                    style: TextStyle(fontSize: 18),
                  ),
                  onPressed: () async {
                    if (_formKey.currentState!.validate()) {
                      await generateResumePDF();
                    }
                  },
                ),
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    nameController.dispose();
    emailController.dispose();
    mobileController.dispose();
    addressController.dispose();
    linkedinController.dispose();
    githubController.dispose();
    objectiveController.dispose();
    educationController.dispose();
    skillsController.dispose();
    experienceController.dispose();
    projectController.dispose();
    certificationController.dispose();
    achievementController.dispose();
    super.dispose();
  }
}