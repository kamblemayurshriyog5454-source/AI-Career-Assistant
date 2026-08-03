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
# Home API
# ============================================

@app.get("/")
async def home():
    return {
        "success": True,
        "message": "AI Career Assistant Backend Running Successfully"
    }

# ============================================
# Models
# ============================================

class ChatRequest(BaseModel):
    question: str


class InterviewAnswer(BaseModel):
    question: str
    answer: str


# ============================================
# Extract Resume Text
# ============================================

def extract_resume_text(file: UploadFile):

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

    os.remove(temp_path)

    return text


# ============================================
# AI Helper
# ============================================

def ask_ai(prompt: str):

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": "You are an expert AI Career Assistant."
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
# Resume Analysis
# ============================================

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):

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
# ATS Score
# ============================================

@app.post("/ats-score")
async def ats_score(file: UploadFile = File(...)):

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
# Job Recommendation
# ============================================

@app.post("/job-recommendation")
async def job_recommendation(file: UploadFile = File(...)):

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
# Skill Gap Analysis
# ============================================

@app.post("/skill-gap")
async def skill_gap(file: UploadFile = File(...)):

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
# Course Recommendation
# ============================================

@app.post("/course-recommendation")
async def course_recommendation(file: UploadFile = File(...)):

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
# Learning Roadmap
# ============================================

@app.post("/learning-roadmap")
async def learning_roadmap(file: UploadFile = File(...)):

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
# Mock Interview Questions
# ============================================

@app.post("/mock-interview")
async def mock_interview(file: UploadFile = File(...)):

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
# Evaluate Interview Answer
# ============================================

@app.post("/evaluate-answer")
async def evaluate_answer(data: InterviewAnswer):

    try:

        prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

Question:
{data.question}

Candidate Answer:
{data.answer}

Return EXACTLY in this format:

Score: X/10

Strengths:
- Point 1
- Point 2

Weaknesses:
- Point 1
- Point 2

Suggested Better Answer:
(Write an ideal answer)

Final Feedback:
(Overall feedback)
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
# AI Career Chatbot
# ============================================

@app.post("/chat")
async def chat(request: ChatRequest):

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
# Health Check
# ============================================

@app.get("/health")
async def health():

    return {
        "success": True,
        "status": "Backend Running",
        "version": "3.0"
    }
# ============================================
# Run Server
# ============================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )                            