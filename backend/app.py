from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI

import tempfile
import json
import os


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================================
# GROQ CLIENT
# ============================================================

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Career Assistant",
    description="AI-powered career guidance and resume analysis API",
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
# DATA MODELS
# ============================================================

class ChatRequest(BaseModel):

    question: str


class InterviewAnswer(BaseModel):

    question: str

    answer: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
async def home():

    return {
        "success": True,
        "message": "AI Career Assistant Backend Running",
        "version": "4.0"
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
# GROQ MODELS
# ============================================================

@app.get("/models")
async def get_models():

    try:

        models = client.models.list()

        return {
            "success": True,

            "models": [
                model.id
                for model in models.data
            ]
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# EXTRACT PDF TEXT
# ============================================================

def extract_resume_text(file: UploadFile):

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp:

            temp.write(file.file.read())

            temp_path = temp.name


        reader = PdfReader(temp_path)

        text = ""


        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"


        return text.strip()


    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


# ============================================================
# AI ENGINE
# ============================================================

def ask_ai(prompt: str):

    if not GROQ_API_KEY:

        raise Exception(
            "GROQ_API_KEY is not configured."
        )


    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",

                "content": """
You are an expert AI Career Assistant.

Your job is to provide accurate, professional,
structured and useful career guidance.

Always use clear headings and bullet points
when appropriate.

Avoid unnecessary repetition.
"""
            },

            {
                "role": "user",

                "content": prompt
            }

        ],

        temperature=0.4,

        max_tokens=2048,
    )


    return response.choices[0].message.content


# ============================================================
# RESUME ANALYSIS
# ============================================================

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)


        if not resume:

            return {
                "success": False,
                "error": "Unable to extract text from resume."
            }


        prompt = f"""
You are an ATS Resume Expert.

Analyze the following resume.

Return a professional report using exactly these sections:

1. ATS SCORE
Give a score out of 100.

2. PROFESSIONAL SUMMARY
Summarize the candidate.

3. TECHNICAL SKILLS
List the important skills.

4. STRENGTHS
List major strengths.

5. WEAKNESSES
List weaknesses or missing areas.

6. RESUME IMPROVEMENTS
Give practical suggestions.

7. CAREER RECOMMENDATION
Suggest suitable career paths.

Resume:

{resume}
"""


        answer = ask_ai(prompt)


        return {
            "success": True,
            "analysis": answer
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
Analyze this resume as an ATS system.

Return:

ATS Score: X/100

Keyword Match:
Formatting:
Technical Skills:
Experience:
Education:

Main Issues:

Recommendations:

Resume:

{resume}
"""


        answer = ask_ai(prompt)


        return {
            "success": True,
            "score": answer
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

Recommend the TOP 10 most suitable jobs.

For every job provide:

Job Title
Match Percentage
Reason
Required Skills

Rank the jobs from highest match to lowest.

Resume:

{resume}
"""


        answer = ask_ai(prompt)


        return {
            "success": True,
            "jobs": answer
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

Analyze the resume for an AI / Data Science career.

Return:

CURRENT SKILLS

STRENGTHS

MISSING SKILLS

HIGH PRIORITY SKILLS

MEDIUM PRIORITY SKILLS

LEARNING SUGGESTIONS

CAREER READINESS

Resume:

{resume}
"""


        answer = ask_ai(prompt)


        return {
            "success": True,
            "analysis": answer
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

Recommend the best learning courses.

Return at least 8 recommendations.

For every course provide:

Course Name
Platform
Skill
Difficulty
Estimated Duration
Reason

Resume:

{resume}
"""


        answer = ask_ai(prompt)


        return {
            "success": True,
            "courses": answer
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
Create a professional career learning roadmap.

Analyze this resume.

Return:

CURRENT LEVEL

CAREER GOAL

MONTH 1

MONTH 2

MONTH 3

MONTH 4

PROJECTS TO BUILD

IMPORTANT TECHNOLOGIES

RECOMMENDED CERTIFICATIONS

INTERVIEW PREPARATION

FINAL ADVICE

Make the roadmap practical.

Resume:

{resume}
"""


        answer = ask_ai(prompt)


        return {
            "success": True,
            "roadmap": answer
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

Read the candidate resume.

Generate EXACTLY 10 interview questions.

Distribution:

5 Technical Questions
3 HR Questions
2 Project Questions

Questions must be relevant to the candidate's
skills, internships, projects and education.

Return ONLY valid JSON.

Format:

[
    "Question 1",
    "Question 2",
    "Question 3",
    "Question 4",
    "Question 5",
    "Question 6",
    "Question 7",
    "Question 8",
    "Question 9",
    "Question 10"
]

Resume:

{resume}
"""


        answer = ask_ai(prompt)


        # --------------------------------------------------------
        # CLEAN AI JSON
        # --------------------------------------------------------

        cleaned = answer.strip()


        if cleaned.startswith("```"):

            cleaned = cleaned.replace(
                "```json",
                ""
            )

            cleaned = cleaned.replace(
                "```",
                ""
            )

            cleaned = cleaned.strip()


        try:

            questions = json.loads(cleaned)


        except Exception:

            questions = [

                q.strip(
                    "-•1234567890. "
                ).strip()

                for q in answer.split("\n")

                if q.strip()
            ]


        if not isinstance(
            questions,
            list
        ):

            raise Exception(
                "Invalid interview question format."
            )


        return {

            "success": True,

            "questions": questions[:10]
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# INTERVIEW ANSWER EVALUATION ENGINE
# ============================================================

def evaluate_answer_with_ai(
    question: str,
    answer: str
):

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

INTERVIEW QUESTION:

{question}


CANDIDATE ANSWER:

{answer}


Evaluate based on:

1. Technical correctness
2. Understanding
3. Relevance
4. Communication
5. Completeness
6. Confidence


Return EXACTLY this structure:

SCORE: X/10

TECHNICAL QUALITY:
Explain the technical quality.

STRENGTHS:
- Strength 1
- Strength 2
- Strength 3

WEAKNESSES:
- Weakness 1
- Weakness 2
- Weakness 3

SUGGESTED BETTER ANSWER:
Write a professional ideal answer.

FINAL FEEDBACK:
Give concise feedback and explain how the candidate
can improve the answer.

Do not change the question.
"""


    return ask_ai(prompt)


# ============================================================
# EVALUATE ANSWER
# ============================================================

@app.post("/evaluate-answer")
async def evaluate_answer(
    data: InterviewAnswer
):

    try:

        question = data.question.strip()

        answer = data.answer.strip()


        if not question:

            return {
                "success": False,
                "error": "Question cannot be empty."
            }


        if not answer:

            return {
                "success": False,
                "error": "Please provide an answer."
            }


        evaluation = evaluate_answer_with_ai(
            question,
            answer
        )


        return {

            "success": True,

            "evaluation": evaluation
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# ALTERNATIVE EVALUATION ROUTES
#
# These make the backend compatible with older
# Flutter versions of your project.
# ============================================================

@app.post("/evaluate")
async def evaluate(
    data: InterviewAnswer
):

    return await evaluate_answer(data)


@app.post("/evaluate_interview")
async def evaluate_interview(
    data: InterviewAnswer
):

    return await evaluate_answer(data)


@app.post("/evaluateAnswer")
async def evaluateAnswer(
    data: InterviewAnswer
):

    return await evaluate_answer(data)


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

Help the user with:

Resume Review
ATS Score
Resume Improvement
Interview Preparation
Job Recommendations
Skill Gap Analysis
Learning Roadmap
Flutter
Python
Java
Data Structures
Artificial Intelligence
Machine Learning
Data Science
Career Guidance

Answer professionally.

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
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "app:app",

        host="0.0.0.0",

        port=8000,

        reload=True,
    )