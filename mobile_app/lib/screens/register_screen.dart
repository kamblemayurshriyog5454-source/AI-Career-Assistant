import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:mobile_app/config/api_config.dart';
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final TextEditingController nameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController mobileController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController confirmPasswordController =
      TextEditingController();

  final FirebaseAuth auth = FirebaseAuth.instance;
  final FirebaseFirestore firestore = FirebaseFirestore.instance;

  bool hidePassword = true;
  bool hideConfirmPassword = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xffF4F6F9),

      appBar: AppBar(
        title: const Text("Create Account"),
        centerTitle: true,
      ),

      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),

        child: Column(
          children: [

            const SizedBox(height: 20),

            const Icon(
              Icons.smart_toy,
              size: 90,
              color: Colors.blue,
            ),

            const SizedBox(height: 20),

            const Text(
              "Create Account",
              style: TextStyle(
                fontSize: 30,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 40),

            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: "Full Name",
                prefixIcon: Icon(Icons.person),
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                labelText: "Email",
                prefixIcon: Icon(Icons.email),
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: mobileController,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: "Mobile Number",
                prefixIcon: Icon(Icons.phone),
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: passwordController,
              obscureText: hidePassword,
              decoration: InputDecoration(
                labelText: "Password",
                prefixIcon: const Icon(Icons.lock),
                suffixIcon: IconButton(
                  icon: Icon(
                    hidePassword
                        ? Icons.visibility
                        : Icons.visibility_off,
                  ),
                  onPressed: () {
                    setState(() {
                      hidePassword = !hidePassword;
                    });
                  },
                ),
                border: const OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: confirmPasswordController,
              obscureText: hideConfirmPassword,
              decoration: InputDecoration(
                labelText: "Confirm Password",
                prefixIcon: const Icon(Icons.lock),
                suffixIcon: IconButton(
                  icon: Icon(
                    hideConfirmPassword
                        ? Icons.visibility
                        : Icons.visibility_off,
                  ),
                  onPressed: () {
                    setState(() {
                      hideConfirmPassword =
                          !hideConfirmPassword;
                    });
                  },
                ),
                border: const OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 30),

            SizedBox(
              width: double.infinity,
              height: 55,

              child: ElevatedButton(
                onPressed: () async {

                  String name = nameController.text.trim();
                  String email = emailController.text.trim();
                  String mobile = mobileController.text.trim();
                  String password = passwordController.text.trim();
                  String confirmPassword =
                      confirmPasswordController.text.trim();

                  if (name.isEmpty ||
                      email.isEmpty ||
                      mobile.isEmpty ||
                      password.isEmpty ||
                      confirmPassword.isEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Please fill all fields"),
                        backgroundColor: Colors.red,
                      ),
                    );
                    return;
                  }

                  if (!email.contains("@") ||
                      !email.contains(".")) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Enter valid email"),
                        backgroundColor: Colors.orange,
                      ),
                    );
                    return;
                  }

                  if (mobile.length != 10) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                            "Mobile must be 10 digits"),
                        backgroundColor: Colors.orange,
                      ),
                    );
                    return;
                  }

                  if (password.length < 6) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                            "Password must be at least 6 characters"),
                        backgroundColor: Colors.orange,
                      ),
                    );
                    return;
                  }

                  if (password != confirmPassword) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content:
                            Text("Passwords do not match"),
                        backgroundColor: Colors.red,
                      ),
                    );
                    return;
                  }

                  try {

                    UserCredential userCredential =
                        await auth.createUserWithEmailAndPassword(
                      email: email,
                      password: password,
                    );

                    String uid = userCredential.user!.uid;

                    await firestore.collection("Users").doc(uid).set({
                       "uid": uid,
                       "name": name,
                       "email": email,
                       "mobile": mobile,
                       "createdAt": FieldValue.serverTimestamp(),
      });

                    if (!mounted) return;

                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                            "Registration Successful"),
                        backgroundColor: Colors.green,
                      ),
                    );

                    Navigator.pop(context);

                  } on FirebaseAuthException catch (e) {

                    String message = e.message ??
                        "Authentication Failed";

                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(message),
                        backgroundColor: Colors.red,
                      ),
                    );

                    debugPrint("FirebaseAuth Error");
                    debugPrint(e.code);
                    debugPrint(e.message);

                  } on FirebaseException catch (e) {

                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                            e.message ?? "Database Error"),
                        backgroundColor: Colors.red,
                      ),
                    );

                    debugPrint("Database Error");
                    debugPrint(e.code);
                    debugPrint(e.message);

                  } catch (e, stackTrace) {

                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(e.toString()),
                        backgroundColor: Colors.red,
                      ),
                    );

                    debugPrint("General Error");
                    debugPrint(e.toString());
                    debugPrintStack(stackTrace: stackTrace);
                  }

                },

                child: const Text(
                  "REGISTER",
                  style: TextStyle(fontSize: 18),
                ),
              ),
            ),

            const SizedBox(height: 20),

            TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text(
                "Already have an account? Login",
              ),
            ),
          ],
        ),
      ),
    );
  }
}