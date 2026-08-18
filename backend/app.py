from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI

import tempfile
import json
import os


# ============================================
# Load Environment Variables
# ============================================

load_dotenv()


# ============================================
# Groq Client
# ============================================

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="AI Career Assistant",
    version="3.0"
)


# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# HOME
# ============================================

@app.get("/")
async def home():

    return {
        "success": True,
        "message": "AI Career Assistant Backend Running Successfully"
    }


# ============================================
# MODELS
# ============================================

class ChatRequest(BaseModel):
    question: str


class InterviewAnswer(BaseModel):
    question: str
    answer: str


# ============================================
# EXTRACT RESUME TEXT
# ============================================

def extract_resume_text(file: UploadFile):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp:

        temp.write(file.file.read())

        temp_path = temp.name

    try:

        reader = PdfReader(temp_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================
# AI HELPER
# ============================================

def ask_ai(prompt: str):

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content":
                "You are an expert AI Career Assistant "
                "and professional technical interviewer."
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


# ============================================
# RESUME ANALYSIS
# ============================================

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
You are an ATS Resume Expert.

Analyze this resume.

Return:

ATS Score (Out of 100)

Professional Summary

Technical Skills

Strengths

Weaknesses

Suggestions to Improve

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


# ============================================
# ATS SCORE
# ============================================

@app.post("/ats-score")
async def ats_score(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
Calculate the ATS score of this resume.

Return ONLY:

ATS Score:
Reason:

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


# ============================================
# JOB RECOMMENDATION
# ============================================

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


# ============================================
# SKILL GAP ANALYSIS
# ============================================

@app.post("/skill-gap")
async def skill_gap(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
You are an AI Career Advisor.

Analyze this resume for an AI Engineer role.

Return in this format:

Overall Match

Strengths

Missing Skills

Learning Suggestions

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


# ============================================
# COURSE RECOMMENDATION
# ============================================

@app.post("/course-recommendation")
async def course_recommendation(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
Analyze this resume.

Recommend the BEST online courses.

For every course provide:

Course Name

Platform

Duration

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


# ============================================
# LEARNING ROADMAP
# ============================================

@app.post("/learning-roadmap")
async def learning_roadmap(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
Create a complete learning roadmap based on this resume.

Include:

Current Level

Career Goal

Month 1

Month 2

Month 3

Month 4

Recommended Certifications

Final Advice

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


# ============================================
# MOCK INTERVIEW
# ============================================

@app.post("/mock-interview")
async def mock_interview(
    file: UploadFile = File(...)
):

    try:

        resume = extract_resume_text(file)

        prompt = f"""
You are an expert Technical Interviewer.

Read the resume carefully.

Generate EXACTLY 10 interview questions.

Rules:

1. 5 Technical Questions
2. 3 HR Questions
3. 2 Project Questions

Return ONLY a valid JSON array.

Example:

[
  "Tell me about yourself.",
  "Explain your final year project.",
  "What is OOP?",
  "Difference between List and Map in Flutter?",
  "What is Firebase?",
  "Explain API integration.",
  "What are your strengths?",
  "What are your weaknesses?",
  "Why should we hire you?",
  "Where do you see yourself in 5 years?"
]

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        try:

            questions = json.loads(answer)

            if not isinstance(questions, list):
                raise Exception()

        except Exception:

            questions = [
                q.strip("-•1234567890. ").strip()
                for q in answer.split("\n")
                if q.strip()
            ]

        return {
            "success": True,
            "questions": questions
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# EVALUATE INTERVIEW ANSWER
# ============================================

async def evaluate_interview_answer(
    data: InterviewAnswer
):

    try:

        # ----------------------------------------
        # VALIDATE QUESTION
        # ----------------------------------------

        if not data.question.strip():

            return {
                "success": False,
                "error": "Interview question is empty."
            }


        # ----------------------------------------
        # VALIDATE ANSWER
        # ----------------------------------------

        if not data.answer.strip():

            return {
                "success": False,
                "error": "Candidate answer is empty."
            }


        # ----------------------------------------
        # AI EVALUATION PROMPT
        # ----------------------------------------

        prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer carefully.

Interview Question:
{data.question}

Candidate Answer:
{data.answer}

Evaluate the answer based on:

1. Technical correctness
2. Understanding
3. Relevance
4. Clarity
5. Completeness
6. Communication

Return EXACTLY in this format:

Score: X/10

Strengths:
- Point 1
- Point 2
- Point 3

Weaknesses:
- Point 1
- Point 2
- Point 3

Suggested Better Answer:
Write a clear and professional ideal answer.

Final Feedback:
Give concise overall feedback and tell the candidate how they can improve.
"""

        answer = ask_ai(prompt)

        return {
            "success": True,
            "evaluation": answer
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# PRIMARY EVALUATION ENDPOINT
# ============================================

@app.post("/evaluate-answer")
async def evaluate_answer(
    data: InterviewAnswer
):

    return await evaluate_interview_answer(data)


# ============================================
# BACKWARD COMPATIBILITY ENDPOINT
#
# If your old Flutter code is calling /evaluate,
# this will also work.
# ============================================

@app.post("/evaluate")
async def evaluate(
    data: InterviewAnswer
):

    return await evaluate_interview_answer(data)


# ============================================
# BACKWARD COMPATIBILITY ENDPOINT
#
# If your Flutter code calls /evaluate_interview,
# this will also work.
# ============================================

@app.post("/evaluate_interview")
async def evaluate_interview(
    data: InterviewAnswer
):

    return await evaluate_interview_answer(data)


# ============================================
# AI CAREER CHATBOT
# ============================================

@app.post("/chat")
async def chat(
    request: ChatRequest
):

    try:

        prompt = f"""
You are an AI Career Assistant.

Help students with:

• Resume Review
• ATS Score
• Resume Improvement
• Interview Preparation
• Job Recommendations
• Skill Gap Analysis
• Learning Roadmap
• Flutter
• Python
• Java
• Data Structures
• AI & Machine Learning
• Career Guidance

Answer professionally and clearly.

Question:

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


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
async def health():

    return {
        "success": True,
        "status": "Backend Running",
        "version": "3.0"
    }


# ============================================
# AVAILABLE GROQ MODELS
# ============================================

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


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )