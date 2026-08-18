from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI

import tempfile
import json
import os
import re


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not configured.")


# ============================================================
# GROQ CLIENT
# ============================================================

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Career Assistant",
    version="4.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
async def home():

    return {
        "success": True,
        "message": "AI Career Assistant Backend Running Successfully",
        "version": "4.0"
    }


# ============================================================
# MODELS
# ============================================================

class ChatRequest(BaseModel):
    question: str


class InterviewAnswer(BaseModel):
    question: str
    answer: str


class InterviewEvaluationRequest(BaseModel):
    resume: str
    questions: list[str]
    answers: list[str]


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_resume_text(file: UploadFile):

    temp_path = None

    try:

        file_content = file.file.read()

        if not file_content:
            raise Exception("Uploaded PDF is empty.")

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp:

            temp.write(file_content)
            temp_path = temp.name

        reader = PdfReader(temp_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise Exception(
                "Could not extract text from the PDF. "
                "Please upload a text-based PDF."
            )

        return text.strip()

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# AI HELPER
# ============================================================

def ask_ai(prompt: str):

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert AI Career Assistant, "
                    "ATS resume expert and technical interviewer. "
                    "Give accurate, professional and useful answers."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3,
        max_tokens=4096,
    )

    return response.choices[0].message.content


# ============================================================
# CLEAN AI JSON
# ============================================================

def clean_json_response(answer: str):

    answer = answer.strip()

    # Remove ```json
    answer = re.sub(
        r"^```json\s*",
        "",
        answer,
        flags=re.IGNORECASE
    )

    # Remove ```
    answer = re.sub(
        r"^```\s*",
        "",
        answer
    )

    answer = re.sub(
        r"\s*```$",
        "",
        answer
    )

    # Find first JSON object
    first_brace = answer.find("{")
    last_brace = answer.rfind("}")

    if first_brace != -1 and last_brace != -1:

        answer = answer[
            first_brace:last_brace + 1
        ]

    return answer.strip()


# ============================================================
# RESUME ANALYSIS
# ============================================================

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
You are a professional ATS resume analyzer.

Analyze the resume below.

IMPORTANT:
Return ONLY valid JSON.

DO NOT use Markdown.
DO NOT use ```json.
DO NOT add explanations outside JSON.

Use EXACTLY this structure:

{{
    "ats_score": 0,

    "professional_summary": "",

    "technical_skills": [],

    "soft_skills": [],

    "education": [
        {{
            "qualification": "",
            "institution": "",
            "year": "",
            "score": ""
        }}
    ],

    "projects": [
        {{
            "name": "",
            "technologies": [],
            "description": "",
            "outcome": ""
        }}
    ],

    "experience": [
        {{
            "role": "",
            "company": "",
            "duration": "",
            "responsibilities": []
        }}
    ],

    "strengths": [],

    "weaknesses": [],

    "suggestions": [],

    "recommended_roles": [
        {{
            "role": "",
            "match_percentage": 0,
            "reason": ""
        }}
    ],

    "final_verdict": ""
}}

RULES:

1. ats_score must be between 0 and 100.

2. professional_summary must be concise and professional.

3. technical_skills must contain skills actually found
   in the resume.

4. soft_skills must contain skills actually supported
   by the resume.

5. education must contain education information.

6. projects must contain project information.

7. experience must contain internship/work information.

8. strengths must contain realistic strengths.

9. weaknesses must contain realistic weaknesses.

10. suggestions must contain practical resume improvements.

11. recommended_roles must contain suitable entry-level
    career roles.

12. match_percentage must be between 0 and 100.

13. final_verdict must be a short professional conclusion.

14. NEVER invent companies, marks, projects,
    technologies or achievements.

15. If information is missing, write:
    "Not specified"

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        cleaned = clean_json_response(answer)

        try:

            analysis = json.loads(cleaned)

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "AI returned invalid JSON.",
                "raw_response": answer
            }

        return {
            "success": True,
            "analysis": analysis
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# ATS SCORE
# ============================================================

@app.post("/ats-score")
async def ats_score(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
Analyze this resume as an ATS expert.

Return ONLY valid JSON:

{{
    "score": 0,
    "reason": "",
    "improvements": []
}}

Score must be between 0 and 100.

Do not invent information.

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        cleaned = clean_json_response(answer)

        try:

            result = json.loads(cleaned)

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "Invalid JSON returned by AI.",
                "raw_response": answer
            }

        return {
            "success": True,
            "score": result
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# JOB RECOMMENDATION
# ============================================================

@app.post("/job-recommendation")
async def job_recommendation(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
Analyze this resume.

Recommend exactly 10 suitable entry-level jobs.

Return ONLY valid JSON:

{{
    "jobs": [
        {{
            "job_title": "",
            "match_percentage": 0,
            "reason": ""
        }}
    ]
}}

Do not invent experience.

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        cleaned = clean_json_response(answer)

        try:

            result = json.loads(cleaned)

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "Invalid JSON returned by AI.",
                "raw_response": answer
            }

        return {
            "success": True,
            "jobs": result.get("jobs", [])
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# SKILL GAP
# ============================================================

@app.post("/skill-gap")
async def skill_gap(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
You are an AI Career Advisor.

Analyze this resume for an AI / Data Science career.

Return ONLY valid JSON:

{{
    "overall_match": 0,
    "strengths": [],
    "missing_skills": [],
    "learning_suggestions": []
}}

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        cleaned = clean_json_response(answer)

        try:

            result = json.loads(cleaned)

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "Invalid JSON returned by AI.",
                "raw_response": answer
            }

        return {
            "success": True,
            "analysis": result
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# COURSE RECOMMENDATION
# ============================================================

@app.post("/course-recommendation")
async def course_recommendation(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
Analyze this resume.

Recommend useful online courses.

Return ONLY valid JSON:

{{
    "courses": [
        {{
            "course_name": "",
            "platform": "",
            "duration": "",
            "reason": ""
        }}
    ]
}}

Recommend realistic courses.

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        cleaned = clean_json_response(answer)

        try:

            result = json.loads(cleaned)

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "Invalid JSON returned by AI.",
                "raw_response": answer
            }

        return {
            "success": True,
            "courses": result.get("courses", [])
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# LEARNING ROADMAP
# ============================================================

@app.post("/learning-roadmap")
async def learning_roadmap(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
Create a personalized career learning roadmap.

Return ONLY valid JSON:

{{
    "current_level": "",
    "career_goal": "",
    "month_1": [],
    "month_2": [],
    "month_3": [],
    "month_4": [],
    "recommended_certifications": [],
    "final_advice": ""
}}

Base everything on the resume.

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        cleaned = clean_json_response(answer)

        try:

            result = json.loads(cleaned)

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "Invalid JSON returned by AI.",
                "raw_response": answer
            }

        return {
            "success": True,
            "roadmap": result
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# MOCK INTERVIEW
# ============================================================

@app.post("/mock-interview")
async def mock_interview(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
You are a professional technical interviewer.

Read the resume carefully.

Generate EXACTLY 10 interview questions.

Question distribution:

5 Technical Questions
3 HR Questions
2 Project Questions

Questions must be directly related to the candidate's
resume, education, projects and internships.

Return ONLY a valid JSON array.

Example:

[
    "Explain your machine learning project.",
    "What is inheritance in Java?",
    "What is your biggest strength?"
]

Do not add numbering.
Do not add explanations.
Do not use Markdown.

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        cleaned = answer.strip()

        # Remove markdown if model accidentally adds it
        cleaned = re.sub(
            r"^```json\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"^```\s*",
            "",
            cleaned
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

        try:

            questions = json.loads(
                cleaned
            )

        except json.JSONDecodeError:

            # Fallback line parsing
            questions = [
                q.strip()
                for q in answer.split("\n")
                if q.strip()
            ]

        if not isinstance(
            questions,
            list
        ):

            raise Exception(
                "AI did not return a valid question list."
            )

        questions = [
            str(q).strip()
            for q in questions
            if str(q).strip()
        ]

        # Keep exactly 10
        questions = questions[:10]

        if len(questions) < 10:

            raise Exception(
                "AI returned fewer than 10 interview questions."
            )

        return {
            "success": True,
            "questions": questions
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# EVALUATE SINGLE ANSWER
# ============================================================

@app.post("/evaluate-answer")
async def evaluate_answer(
    data: InterviewAnswer
):

    try:

        prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

Question:
{data.question}

Candidate Answer:
{data.answer}

Return ONLY valid JSON:

{{
    "score": 0,
    "strengths": [],
    "weaknesses": [],
    "better_answer": "",
    "feedback": ""
}}

Score must be between 0 and 10.

Be professional and constructive.
"""

        answer = ask_ai(prompt)

        cleaned = clean_json_response(answer)

        try:

            result = json.loads(cleaned)

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "Invalid JSON returned by AI.",
                "raw_response": answer
            }

        return {
            "success": True,
            "evaluation": result
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# COMPLETE INTERVIEW EVALUATION
# ============================================================

@app.post("/evaluate-interview")
async def evaluate_interview(
    data: InterviewEvaluationRequest
):

    try:

        if len(data.questions) == 0:

            raise Exception(
                "No interview questions received."
            )

        if len(data.questions) != len(data.answers):

            raise Exception(
                "Questions and answers count do not match."
            )

        # Build interview transcript
        interview_text = ""

        for i in range(
            len(data.questions)
        ):

            question = data.questions[i]
            answer = data.answers[i]

            interview_text += f"""

Question {i + 1}:
{question}

Candidate Answer:
{answer if answer.strip() else "No answer provided."}

"""

        prompt = f"""
You are a senior technical interviewer.

Evaluate the candidate's COMPLETE mock interview.

Resume:

{data.resume}

Interview:

{interview_text}

IMPORTANT:
Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "overall_score": 0,

    "technical_score": 0,

    "hr_score": 0,

    "project_score": 0,

    "technical_feedback": "",

    "hr_feedback": "",

    "strengths": [],

    "weaknesses": [],

    "improvements": [],

    "question_evaluations": [
        {{
            "question_number": 1,
            "score": 0,
            "feedback": "",
            "better_answer": ""
        }}
    ],

    "final_verdict": ""
}}

RULES:

1. overall_score must be between 0 and 10.

2. technical_score must be between 0 and 10.

3. hr_score must be between 0 and 10.

4. project_score must be between 0 and 10.

5. Evaluate every question.

6. question_evaluations must contain one object
   for every question.

7. Score every answer between 0 and 10.

8. Consider an unanswered question as 0.

9. Give constructive feedback.

10. Do not invent candidate experience.

11. final_verdict should clearly explain whether
    the candidate appears ready for an entry-level role.

12. Return ONLY JSON.
"""

        answer = ask_ai(prompt)

        cleaned = clean_json_response(answer)

        try:

            result = json.loads(cleaned)

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "AI returned invalid evaluation JSON.",
                "raw_response": answer
            }

        return {
            "success": True,

            "overall_score":
                result.get(
                    "overall_score",
                    0
                ),

            "technical_score":
                result.get(
                    "technical_score",
                    0
                ),

            "hr_score":
                result.get(
                    "hr_score",
                    0
                ),

            "project_score":
                result.get(
                    "project_score",
                    0
                ),

            "technical_feedback":
                result.get(
                    "technical_feedback",
                    ""
                ),

            "hr_feedback":
                result.get(
                    "hr_feedback",
                    ""
                ),

            "strengths":
                result.get(
                    "strengths",
                    []
                ),

            "weaknesses":
                result.get(
                    "weaknesses",
                    []
                ),

            "improvements":
                result.get(
                    "improvements",
                    []
                ),

            "question_evaluations":
                result.get(
                    "question_evaluations",
                    []
                ),

            "final_verdict":
                result.get(
                    "final_verdict",
                    ""
                )
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# AI CAREER CHATBOT
# ============================================================

@app.post("/chat")
async def chat(
    request: ChatRequest
):

    try:

        prompt = f"""
You are an AI Career Assistant.

Help students with:

- Resume Review
- ATS Score
- Resume Improvement
- Interview Preparation
- Job Recommendations
- Skill Gap Analysis
- Learning Roadmap
- Flutter
- Python
- Java
- Data Structures
- Artificial Intelligence
- Machine Learning
- Data Science
- Career Guidance

Answer professionally, clearly and concisely.

User Question:

{request.question}
"""

        answer = ask_ai(prompt)

        return {
            "success": True,
            "answer": answer
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "success": True,
        "status": "Backend Running",
        "version": "4.0"
    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )