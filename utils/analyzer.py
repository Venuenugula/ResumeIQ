from google import genai
from dotenv import load_dotenv
import os, json, re, time

load_dotenv()
def get_api_key():
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=get_api_key())
MODEL = "gemini-2.5-flash"

def call_gemini(prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = 30 * (attempt + 1)
                print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}...")
                time.sleep(wait)
            else:
                raise e

def parse_json(raw: str) -> dict:
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw.strip())

def analyze_match(resume_chunks: str, jd_text: str) -> dict:
    prompt = f"""
You are an expert technical recruiter and ATS system.

Analyze the candidate's resume excerpts against the job description below.
Respond ONLY with a valid JSON object — no markdown, no explanation, no code fences.

Resume excerpts:
{resume_chunks}

Job Description:
{jd_text}

Return this exact JSON structure:
{{
  "match_score": <integer 0-100>,
  "matched_skills": [<list of skills the candidate has that match the JD>],
  "missing_skills": [<list of skills in the JD missing from the resume>],
  "strengths": [<2-3 strongest points about this candidate for this role>],
  "improvements": [<2-3 specific actionable resume improvements for this JD>],
  "verdict": "<one sentence summary of overall fit>"
}}
"""
    return parse_json(call_gemini(prompt))