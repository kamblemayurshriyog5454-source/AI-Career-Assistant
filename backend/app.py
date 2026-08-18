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
    version="4.0",
    description="AI Career Assistant Backend",
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
# CONFIGURATION
# ============================================================

AI_MODEL = "openai/gpt-oss-120b"


# ============================================================
# HOME
# ============================================================

@app.get("/")
async def home():

    return {
        "success": True,
        "message": "AI Career Assistant Backend Running Successfully",
        "version": "4.0",
        "model": AI_MODEL,
    }


# ============================================================
# DATA MODELS
# ============================================================

class ChatRequest(BaseModel):
    question: str


class InterviewAnswer(BaseModel):
    question: str
    answer: str


class InterviewEvaluationRequest(BaseModel):
    resume: str = ""
    questions: list[str]
    answers: list[str]


# ============================================================
# RESUME TEXT EXTRACTION
# ============================================================

async def extract_resume_text(file: UploadFile) -> str:

    temp_path = None

    try:

        content = await file.read()

        if not content:
            raise Exception("Uploaded PDF is empty.")

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp:

            temp.write(content)
            temp_path = temp.name

        reader = PdfReader(temp_path)

        text = ""

        for page in reader.pages:

            try:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            except Exception as e:

                print(
                    f"PDF page extraction error: {e}"
                )

        text = text.strip()

        if not text:

            raise Exception(
                "Could not extract text from the PDF. "
                "Please upload a text-based PDF."
            )

        return text

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)
            except Exception:
                pass


# ============================================================
# AI HELPER
# ============================================================

def ask_ai(
    prompt: str,
    temperature: float = 0.4,
    max_tokens: int = 4096,
) -> str:

    if not GROQ_API_KEY:

        raise Exception(
            "GROQ_API_KEY is not configured on the server."
        )

    response = client.chat.completions.create(

        model=AI_MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert AI Career Assistant, "
                    "professional interviewer and career advisor."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        temperature=temperature,
        max_tokens=max_tokens,
    )

    if not response.choices:

        raise Exception(
            "AI returned an empty response."
        )

    answer = response.choices[0].message.content

    if not answer:

        raise Exception(
            "AI returned an empty answer."
        )

    return answer.strip()


# ============================================================
# JSON CLEANER
# ============================================================

def clean_json_response(text: str):

    text = text.strip()

    # Remove markdown code blocks
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^```\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    text = text.strip()

    return json.loads(text)


# ============================================================
# RESUME ANALYSIS
# ============================================================

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...)
):

    try:

        resume = await extract_resume_text(file)

        prompt = f"""
You are an ATS Resume Expert.

Analyze the following resume professionally.

Return the following sections:

1. ATS Score (Out of 100)

2. Professional Summary

3. Technical Skills

4. Soft Skills

5. Education

6. Projects

7. Experience

8. Strengths

9. Weaknesses

10. Suggestions to Improve

11. Recommended Career Roles

Keep the report clear and suitable for an early-career student.

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        return {
            "success": True,
            "analysis": answer,
        }

    except Exception as e:

        print(
            f"Resume Analysis Error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# ATS SCORE
# ============================================================

@app.post("/ats-score")
async def ats_score(
    file: UploadFile = File(...)
):

    try:

        resume = await extract_resume_text(file)

        prompt = f"""
Analyze this resume as an ATS system.

Return exactly:

ATS Score: X/100

Reason:
Give a clear explanation.

Missing Keywords:
- keyword 1
- keyword 2
- keyword 3

Improvement Suggestions:
- suggestion 1
- suggestion 2
- suggestion 3

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        return {
            "success": True,
            "score": answer,
        }

    except Exception as e:

        print(
            f"ATS Score Error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# JOB RECOMMENDATION
# ============================================================

@app.post("/job-recommendation")
async def job_recommendation(
    file: UploadFile = File(...)
):

    try:

        resume = await extract_resume_text(file)

        prompt = f"""
Analyze this resume.

Recommend the TOP 10 most suitable career roles.

For every role provide:

Job Title:
Match Percentage:
Why It Matches:
Required Skills:
Skills Missing:

Rank the jobs from highest match to lowest match.

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        return {
            "success": True,
            "jobs": answer,
        }

    except Exception as e:

        print(
            f"Job Recommendation Error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# SKILL GAP
# ============================================================

@app.post("/skill-gap")
async def skill_gap(
    file: UploadFile = File(...)
):

    try:

        resume = await extract_resume_text(file)

        prompt = f"""
You are an AI Career Advisor.

Analyze this resume for a career in
Artificial Intelligence and Data Science.

Return:

Overall Match:

Current Skills:
- ...

Missing Skills:
- ...

Technical Skill Gaps:
- ...

Recommended Skills:
- ...

Learning Suggestions:
- ...

Priority:
High:
Medium:
Low:

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        return {
            "success": True,
            "analysis": answer,
        }

    except Exception as e:

        print(
            f"Skill Gap Error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# COURSE RECOMMENDATION
# ============================================================

@app.post("/course-recommendation")
async def course_recommendation(
    file: UploadFile = File(...)
):

    try:

        resume = await extract_resume_text(file)

        prompt = f"""
Analyze this resume.

Recommend the BEST online courses for improving
the candidate's career.

Recommend around 8 courses.

For every course provide:

Course Name:
Platform:
Level:
Duration:
Skills Learned:
Reason:

Prefer well-known learning platforms.

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        return {
            "success": True,
            "courses": answer,
        }

    except Exception as e:

        print(
            f"Course Recommendation Error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# LEARNING ROADMAP
# ============================================================

@app.post("/learning-roadmap")
async def learning_roadmap(
    file: UploadFile = File(...)
):

    try:

        resume = await extract_resume_text(file)

        prompt = f"""
Create a professional learning roadmap
based on this resume.

The candidate is an early-career student.

Return:

Current Level:

Career Goal:

Month 1:
Topics:
Projects:

Month 2:
Topics:
Projects:

Month 3:
Topics:
Projects:

Month 4:
Topics:
Projects:

Recommended Certifications:

Portfolio Projects:

Interview Preparation:

Final Advice:

Resume:

{resume}
"""

        answer = ask_ai(prompt)

        return {
            "success": True,
            "roadmap": answer,
        }

    except Exception as e:

        print(
            f"Learning Roadmap Error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# MOCK INTERVIEW
# ============================================================

@app.post("/mock-interview")
async def mock_interview(
    file: UploadFile = File(...)
):

    try:

        resume = await extract_resume_text(file)

        prompt = f"""
You are an expert technical interviewer.

Read the candidate resume carefully.

Generate EXACTLY 10 interview questions.

Distribution:

5 Technical Questions
3 HR Questions
2 Project / Resume Questions

Questions must be personalized to the resume.

Return ONLY a valid JSON array.

Example:

[
  "Explain your final year project.",
  "What is supervised learning?",
  "Explain OOP concepts in Java.",
  "What are your strengths?",
  "Where do you see yourself in five years?"
]

Resume:

{resume}
"""

        answer = ask_ai(
            prompt,
            temperature=0.3,
            max_tokens=3000,
        )

        questions = []

        try:

            parsed = clean_json_response(
                answer
            )

            if isinstance(parsed, list):

                questions = [
                    str(q).strip()
                    for q in parsed
                    if str(q).strip()
                ]

        except Exception:

            # Fallback if AI doesn't return valid JSON

            lines = answer.split("\n")

            for line in lines:

                cleaned = re.sub(
                    r"^\s*[\d\-\*\.\)]+\s*",
                    "",
                    line,
                ).strip()

                if cleaned:

                    questions.append(
                        cleaned
                    )

        # Keep maximum 10
        questions = questions[:10]

        if len(questions) == 0:

            raise Exception(
                "AI did not return interview questions."
            )

        return {

            "success": True,

            # Flutter uses this
            "resume": resume,

            "questions": questions,
        }

    except Exception as e:

        print(
            f"Mock Interview Error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# INDIVIDUAL ANSWER EVALUATION
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

Return exactly:

Score: X/10

Strengths:
- Point 1
- Point 2

Weaknesses:
- Point 1
- Point 2

Suggested Better Answer:
Write a professional ideal answer.

Final Feedback:
Give concise feedback.
"""

        answer = ask_ai(
            prompt,
            temperature=0.3,
            max_tokens=2000,
        )

        return {
            "success": True,
            "evaluation": answer,
        }

    except Exception as e:

        print(
            f"Answer Evaluation Error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# COMPLETE INTERVIEW EVALUATION
# ============================================================

@app.post("/evaluate-interview")
async def evaluate_interview(
    data: InterviewEvaluationRequest
):

    try:

        # ----------------------------------------------------
        # Validate questions and answers
        # ----------------------------------------------------

        if not data.questions:

            raise Exception(
                "No interview questions received."
            )

        if not data.answers:

            raise Exception(
                "No interview answers received."
            )

        # ----------------------------------------------------
        # Build interview transcript
        # ----------------------------------------------------

        interview_text = ""

        for i, question in enumerate(
            data.questions
        ):

            answer = ""

            if i < len(data.answers):

                answer = data.answers[i]

            if not answer.strip():

                answer = "No answer provided."

            interview_text += f"""

Question {i + 1}:
{question}

Candidate Answer:
{answer}

"""


        # ----------------------------------------------------
        # AI EVALUATION
        # ----------------------------------------------------

        prompt = f"""
You are a senior technical interviewer.

Evaluate this complete mock interview.

Candidate Resume:
{data.resume}

Interview:

{interview_text}

The candidate is an early-career student.

Evaluate:

1. Technical knowledge
2. Communication
3. Problem solving
4. Confidence
5. HR responses
6. Project knowledge
7. Overall interview performance

Calculate an overall score from 0 to 10.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_score": "8/10",
    "technical_feedback": "Detailed technical performance feedback.",
    "hr_feedback": "Detailed HR and communication feedback.",
    "strengths": [
        "Strength 1",
        "Strength 2",
        "Strength 3"
    ],
    "weaknesses": [
        "Weakness 1",
        "Weakness 2",
        "Weakness 3"
    ],
    "improvements": [
        "Improvement 1",
        "Improvement 2",
        "Improvement 3"
    ],
    "final_verdict": "Professional final interview verdict.",
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2",
        "Recommendation 3"
    ]
}}

Do not add markdown.
Do not add ```json.
Return only JSON.
"""

        answer = ask_ai(
            prompt,
            temperature=0.2,
            max_tokens=4000,
        )

        # ----------------------------------------------------
        # PARSE AI JSON
        # ----------------------------------------------------

        try:

            result = clean_json_response(
                answer
            )

        except Exception as json_error:

            print(
                "AI returned invalid JSON."
            )

            print(
                f"Raw AI response: {answer}"
            )

            # ------------------------------------------------
            # Fallback evaluation
            # ------------------------------------------------

            result = {

                "overall_score": "7/10",

                "technical_feedback": answer,

                "hr_feedback":
                    "The candidate completed the mock interview. "
                    "Communication should continue to be improved "
                    "through regular practice.",

                "strengths": [
                    "Completed the interview.",
                    "Demonstrated technical interest.",
                    "Provided responses to interview questions.",
                ],

                "weaknesses": [
                    "Some answers may require more technical depth.",
                    "Communication can be made more structured.",
                    "More project-specific examples would improve responses.",
                ],

                "improvements": [
                    "Practice explaining technical concepts clearly.",
                    "Use real project examples in answers.",
                    "Practice common HR interview questions.",
                ],

                "final_verdict":
                    "The candidate shows good potential "
                    "for an early-career technical role. "
                    "Further interview practice is recommended.",

                "recommendations": [
                    "Practice technical interview questions.",
                    "Improve project explanation skills.",
                    "Practice concise HR responses.",
                ],
            }

        # ----------------------------------------------------
        # Normalize response
        # ----------------------------------------------------

        overall_score = str(
            result.get(
                "overall_score",
                "7/10"
            )
        )

        technical_feedback = str(
            result.get(
                "technical_feedback",
                "No technical feedback available."
            )
        )

        hr_feedback = str(
            result.get(
                "hr_feedback",
                "No HR feedback available."
            )
        )

        strengths = result.get(
            "strengths",
            []
        )

        weaknesses = result.get(
            "weaknesses",
            []
        )

        improvements = result.get(
            "improvements",
            []
        )

        recommendations = result.get(
            "recommendations",
            []
        )

        final_verdict = str(
            result.get(
                "final_verdict",
                "Keep practicing and improving your interview skills."
            )
        )

        # ----------------------------------------------------
        # Convert lists to strings
        # ----------------------------------------------------

        if isinstance(
            strengths,
            list
        ):

            strengths_text = "\n".join(
                f"• {str(x)}"
                for x in strengths
            )

        else:

            strengths_text = str(
                strengths
            )


        if isinstance(
            weaknesses,
            list
        ):

            weaknesses_text = "\n".join(
                f"• {str(x)}"
                for x in weaknesses
            )

        else:

            weaknesses_text = str(
                weaknesses
            )


        if isinstance(
            improvements,
            list
        ):

            improvements_text = "\n".join(
                f"• {str(x)}"
                for x in improvements
            )

        else:

            improvements_text = str(
                improvements
            )


        if isinstance(
            recommendations,
            list
        ):

            recommendations_text = "\n".join(
                f"• {str(x)}"
                for x in recommendations
            )

        else:

            recommendations_text = str(
                recommendations
            )


        # ----------------------------------------------------
        # Final response for Flutter
        # ----------------------------------------------------

        return {

            "success": True,

            "overall_score":
                overall_score,

            "technical_feedback":
                technical_feedback,

            "hr_feedback":
                hr_feedback,

            "strengths":
                strengths_text,

            "weaknesses":
                weaknesses_text,

            "improvements":
                improvements_text,

            "final_verdict":
                final_verdict,

            "recommendations":
                recommendations_text,

            # Complete report
            "evaluation":
                f"""
OVERALL SCORE
{overall_score}

TECHNICAL PERFORMANCE
{technical_feedback}

HR & COMMUNICATION
{hr_feedback}

STRENGTHS
{strengths_text}

WEAKNESSES
{weaknesses_text}

AREAS FOR IMPROVEMENT
{improvements_text}

RECOMMENDATIONS
{recommendations_text}

FINAL VERDICT
{final_verdict}
""".strip(),
        }

    except Exception as e:

        print(
            f"Complete Interview Evaluation Error: {e}"
        )

        return {

            "success": False,

            "error": str(e),
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
• Artificial Intelligence
• Machine Learning
• Data Science
• Career Guidance

Answer professionally.

Keep the answer clear and practical.

Question:

{request.question}
"""

        answer = ask_ai(
            prompt,
            temperature=0.5,
            max_tokens=2500,
        )

        return {

            "success": True,

            "answer": answer,
        }

    except Exception as e:

        print(
            f"Chat Error: {e}"
        )

        return {

            "success": False,

            "error": str(e),
        }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {

        "success": True,

        "status":
            "Backend Running",

        "version":
            "4.0",

        "model":
            AI_MODEL,

        "endpoints": [

            "/",

            "/health",

            "/analyze",

            "/ats-score",

            "/job-recommendation",

            "/skill-gap",

            "/course-recommendation",

            "/learning-roadmap",

            "/mock-interview",

            "/evaluate-answer",

            "/evaluate-interview",

            "/chat",
        ],
    }


# ============================================================
# RUN SERVER LOCALLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "app:app",

        host="0.0.0.0",

        port=8000,

        reload=True,
    )