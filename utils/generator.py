from utils.analyzer import call_gemini
import json, re


def _parse_json(raw: str):
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw.strip())


def generate_cover_letter(resume_chunks: str, jd_text: str, analysis: dict) -> str:
    prompt = f"""
You are an expert career coach writing a cover letter for a fresher/student.

Candidate resume excerpts:
{resume_chunks}

Job Description:
{jd_text}

Match analysis:
- Match score: {analysis['match_score']}%
- Matched skills: {', '.join(analysis['matched_skills'])}
- Strengths: {', '.join(analysis['strengths'])}

Write a professional, genuine, concise cover letter (3 paragraphs max).
- Paragraph 1: Hook — who they are and why they're excited about this specific role
- Paragraph 2: 2-3 strongest matching projects/skills with specific metrics
- Paragraph 3: Closing — eager to contribute, call to action

Tone: Humble, confident, specific. No generic filler sentences.
Do NOT include subject line or date. Start directly with "Dear Hiring Manager,"
"""
    return call_gemini(prompt)


def generate_interview_questions(resume_chunks: str, jd_text: str, analysis: dict) -> list:
    prompt = f"""
You are an expert technical interviewer preparing a fresher for a job interview.

Candidate resume excerpts:
{resume_chunks}

Job Description:
{jd_text}

Missing skills: {', '.join(analysis.get('missing_skills', []))}
Matched skills: {', '.join(analysis['matched_skills'])}

Generate exactly 10 interview questions most likely to be asked for this specific candidate and role.
Mix of: technical questions on their projects, gap questions on missing skills, behavioural questions.

Respond ONLY with a valid JSON array — no markdown, no explanation, no code fences.

Return this exact structure:
[
  {{
    "question": "<the interview question>",
    "type": "<Technical | Behavioural | Gap>",
    "tip": "<one sentence advice on how to answer based on the candidate's background>"
  }}
]
"""
    return _parse_json(call_gemini(prompt))


def rewrite_bullets(bullets_text: str, jd_text: str, resume_chunks: str) -> list:
    prompt = f"""
You are an expert resume writer and ATS optimization specialist.

The candidate wants to improve their resume bullet points for this job description:
{jd_text}

Candidate background context:
{resume_chunks}

Original bullets to rewrite:
{bullets_text}

Rules for rewriting:
- Start each bullet with a strong action verb
- Add specific metrics or outcomes where possible
- Use keywords from the job description naturally
- Keep each bullet to 1-2 lines max
- Make them ATS-friendly

Respond ONLY with a valid JSON array — no markdown, no explanation, no code fences.

Return this exact structure:
[
  {{
    "original": "<the original bullet text>",
    "rewritten": "<the improved bullet text>"
  }}
]
"""
    return _parse_json(call_gemini(prompt))


def generate_linkedin_summary(resume_chunks: str, jd_text: str, analysis: dict) -> str:
    prompt = f"""
You are a LinkedIn profile expert helping a fresher write their About section.

Candidate resume excerpts:
{resume_chunks}

Target role context:
{jd_text}

Top strengths:
{', '.join(analysis['strengths'])}

Write a compelling LinkedIn About section (250-300 words) that:
- Opens with a strong hook (not "I am a...")
- Highlights 2-3 key projects with real metrics
- Mentions their tech stack naturally
- Ends with what kind of opportunities they're open to
- Sounds human, not robotic

Tone: Confident, genuine, enthusiastic. Written in first person.
"""
    return call_gemini(prompt)


def scan_ats_keywords(resume_chunks: str, jd_text: str) -> dict:
    prompt = f"""
You are an ATS (Applicant Tracking System) expert.

Analyze the job description and resume excerpts below.
Extract the most important keywords and phrases from the JD.
Check which ones are present or missing in the resume.

Job Description:
{jd_text}

Resume excerpts:
{resume_chunks}

Respond ONLY with a valid JSON object — no markdown, no explanation, no code fences.

Return this exact structure:
{{
  "present": [<list of important JD keywords found in the resume>],
  "missing": [<list of important JD keywords NOT found in the resume>],
  "tip": "<one specific tip on which missing keyword to prioritize adding>"
}}
"""
    return _parse_json(call_gemini(prompt))


def compare_multiple_jds(resume_text: str, jds: list) -> list:
    from utils.rag import build_vectorstore, retrieve_relevant_chunks
    from utils.analyzer import analyze_match

    results = []
    vectorstore = build_vectorstore(resume_text)

    for jd_name, jd_text in jds:
        chunks = retrieve_relevant_chunks(vectorstore, jd_text)
        analysis = analyze_match(chunks, jd_text)
        results.append({
            "jd_name":        jd_name,
            "match_score":    analysis["match_score"],
            "matched_skills": analysis["matched_skills"],
            "missing_skills": analysis["missing_skills"],
            "verdict":        analysis["verdict"],
        })

    return results