import streamlit as st
from utils.parser import extract_text_from_pdf
from utils.rag import build_vectorstore, retrieve_relevant_chunks
from utils.analyzer import analyze_match
from utils.generator import (
    generate_cover_letter,
    generate_interview_questions,
    rewrite_bullets,
    generate_linkedin_summary,
    scan_ats_keywords,
    compare_multiple_jds,
)

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL STYLES ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── fonts & base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── hero banner ── */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 2rem;
    color: white;
}
.hero h1 { font-size: 2.8rem; font-weight: 700; margin: 0; letter-spacing: -1px; }
.hero p  { font-size: 1.1rem; opacity: 0.9; margin: 0.5rem 0 0; }

/* ── score ring ── */
.score-container {
    text-align: center;
    padding: 1.5rem;
    border-radius: 16px;
    background: var(--background-color);
    border: 1px solid rgba(128,128,128,0.2);
}
.score-ring {
    width: 140px; height: 140px;
    margin: 0 auto 0.75rem;
    position: relative;
}
.score-ring svg { transform: rotate(-90deg); }
.score-number {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 2rem; font-weight: 700;
}
.score-label { font-size: 0.85rem; color: #666; font-weight: 500; }

/* ── skill badges ── */
.badge-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.badge {
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.82rem; font-weight: 500;
    display: inline-block;
}
.badge-green  { background: #d4edda; color: #155724; }
.badge-red    { background: #f8d7da; color: #721c24; }
.badge-blue   { background: #d1ecf1; color: #0c5460; }
.badge-purple { background: #e2d9f3; color: #4a2080; }
.badge-orange { background: #fff3cd; color: #856404; }

/* ── section cards ── */
.card {
    background: var(--background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    color: var(--text-color);
}

/* ── verdict box ── */
.verdict {
    background: linear-gradient(135deg, #667eea15, #764ba215);
    border-left: 4px solid #667eea;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    font-size: 1rem;
    font-style: italic;
    color: var(--text-color);
    margin: 1rem 0;
}

/* ── tab styling ── */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 8px 20px;
    font-weight: 500;
}

/* ── primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border: none; color: white;
    border-radius: 10px;
    font-weight: 600; font-size: 1rem;
    padding: 0.6rem 2rem;
    transition: opacity 0.2s;
}
.stButton > button[kind="primary"]:hover { opacity: 0.9; }

/* ── rewriter card ── */
.bullet-old { background: #fff0f0; border-left: 3px solid #e74c3c; padding: 8px 12px; border-radius: 0 8px 8px 0; font-size: 0.9rem; margin-bottom: 4px; }
.bullet-new { background: #f0fff4; border-left: 3px solid #27ae60; padding: 8px 12px; border-radius: 0 8px 8px 0; font-size: 0.9rem; }

/* ── footer ── */
.footer { text-align: center; color: #999; font-size: 0.82rem; padding: 2rem 0 0.5rem; }
</style>
""", unsafe_allow_html=True)


# ─── HERO ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🧠 ResumeIQ</h1>
    <p>AI-powered resume analyzer · Match score · Gap analysis · Cover letter · Interview prep</p>
</div>
""", unsafe_allow_html=True)


# ─── HELPERS ────────────────────────────────────────────────────────────────
def score_color(score):
    if score >= 75: return "#27ae60", "#d4edda"
    if score >= 50: return "#f39c12", "#fff3cd"
    return "#e74c3c", "#f8d7da"

def render_score_ring(score):
    color, _ = score_color(score)
    r = 58
    circ = 2 * 3.14159 * r
    dash = (score / 100) * circ
    st.markdown(f"""
    <div class="score-container">
        <div class="score-ring">
            <svg width="140" height="140" viewBox="0 0 140 140">
                <circle cx="70" cy="70" r="{r}" fill="none" stroke="#eee" stroke-width="12"/>
                <circle cx="70" cy="70" r="{r}" fill="none" stroke="{color}" stroke-width="12"
                    stroke-dasharray="{dash:.1f} {circ:.1f}"
                    stroke-linecap="round"
                    style="transition: stroke-dasharray 1s ease"/>
            </svg>
            <div class="score-number" style="color:{color}">{score}</div>
        </div>
        <div class="score-label">Match Score</div>
    </div>
    """, unsafe_allow_html=True)

def render_badges(items, style="badge-green"):
    if not items:
        st.markdown("_None found_")
        return
    badges = " ".join([f'<span class="badge {style}">{s}</span>' for s in items])
    st.markdown(f'<div class="badge-wrap">{badges}</div>', unsafe_allow_html=True)


# ─── INPUT SECTION ──────────────────────────────────────────────────────────
with st.container():
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📄 Your Resume")
        resume_file = st.file_uploader(
            "Upload PDF resume", type=["pdf"],
            label_visibility="collapsed"
        )
        if resume_file:
            st.success(f"✅ {resume_file.name} uploaded")

    with col2:
        st.markdown("### 📋 Job Description")
        jd_text = st.text_area(
            "Paste job description",
            placeholder="Paste the full job description here...",
            height=160,
            label_visibility="collapsed"
        )

analyze_clicked = st.button(
    "🚀 Analyze My Resume",
    use_container_width=True,
    type="primary"
)

if analyze_clicked:
    if not resume_file:
        st.error("Please upload your resume PDF.")
    elif not jd_text.strip():
        st.error("Please paste a job description.")
    else:
        prog = st.progress(0, text="Reading resume...")
        resume_text = extract_text_from_pdf(resume_file)
        prog.progress(25, text="Building RAG pipeline...")
        vectorstore = build_vectorstore(resume_text)
        chunks = retrieve_relevant_chunks(vectorstore, jd_text)
        prog.progress(60, text="Analyzing with Gemini...")
        analysis = analyze_match(chunks, jd_text)
        prog.progress(100, text="Done!")
        prog.empty()

        st.session_state["analysis"]     = analysis
        st.session_state["chunks"]       = chunks
        st.session_state["jd_text"]      = jd_text
        st.session_state["resume_text"]  = resume_text
        st.session_state["vectorstore"]  = vectorstore
        for k in ["cover_letter", "questions", "rewrites", "linkedin", "ats", "comparisons"]:
            st.session_state.pop(k, None)

        st.success("✅ Analysis complete! Scroll down to see results.")


# ─── RESULTS ────────────────────────────────────────────────────────────────
if "analysis" in st.session_state:
    analysis     = st.session_state["analysis"]
    chunks       = st.session_state["chunks"]
    jd_text      = st.session_state["jd_text"]
    resume_text  = st.session_state["resume_text"]

    st.divider()

    # ── score row ──
    c1, c2, c3, c4 = st.columns([1.2, 1, 1, 2])
    with c1: render_score_ring(analysis["match_score"])
    with c2:
        st.metric("✅ Matched", len(analysis["matched_skills"]))
        st.metric("❌ Missing", len(analysis["missing_skills"]))
    with c3:
        st.metric("💪 Strengths", len(analysis["strengths"]))
        st.metric("🔧 Improvements", len(analysis["improvements"]))
    with c4:
        st.markdown(f'<div class="verdict">{analysis["verdict"]}</div>', unsafe_allow_html=True)

    st.divider()

    # ── tabs ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Gap Analysis",
        "💪 Strengths",
        "✉️ Cover Letter",
        "🎯 Interview Prep",
        "✏️ Bullet Rewriter",
        "🔗 LinkedIn Summary",
        "🏆 Multi-JD Compare",
    ])

    # ── TAB 1: Gap Analysis ──────────────────────────────────────────────────
    with tab1:
        st.markdown("#### ATS Keyword Scanner")
        if st.button("🔍 Scan ATS Keywords", key="ats_btn"):
            with st.spinner("Scanning keywords..."):
                st.session_state["ats"] = scan_ats_keywords(chunks, jd_text)

        if "ats" in st.session_state:
            ats = st.session_state["ats"]
            ca, cb = st.columns(2)
            with ca:
                st.markdown("**✅ Keywords found in resume**")
                render_badges(ats.get("present", []), "badge-green")
            with cb:
                st.markdown("**❌ Keywords missing — add these!**")
                render_badges(ats.get("missing", []), "badge-red")
            if ats.get("tip"):
                st.info(f"💡 {ats['tip']}")

        st.markdown("---")
        st.markdown("#### Skill Match Breakdown")
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**✅ Matched Skills**")
            render_badges(analysis["matched_skills"], "badge-green")
        with cb:
            st.markdown("**❌ Missing Skills**")
            if analysis["missing_skills"]:
                render_badges(analysis["missing_skills"], "badge-red")
            else:
                st.success("🎉 No missing skills — perfect match!")

    # ── TAB 2: Strengths ─────────────────────────────────────────────────────
    with tab2:
        ca, cb = st.columns(2)
        with ca:
            st.markdown("#### 💪 Your Strengths")
            for s in analysis["strengths"]:
                st.markdown(f'<div class="card">✅ {s}</div>', unsafe_allow_html=True)
        with cb:
            st.markdown("#### 🔧 Resume Improvements")
            for imp in analysis["improvements"]:
                st.markdown(f'<div class="card">⚠️ {imp}</div>', unsafe_allow_html=True)

    # ── TAB 3: Cover Letter ──────────────────────────────────────────────────
    with tab3:
        st.markdown("#### ✉️ AI-Generated Cover Letter")
        st.caption("Tailored to your resume and this specific job description.")
        if st.button("✨ Generate Cover Letter", key="cl_btn"):
            with st.spinner("Writing your cover letter..."):
                st.session_state["cover_letter"] = generate_cover_letter(
                    chunks, jd_text, analysis
                )
        if "cover_letter" in st.session_state:
            st.text_area(
                "Your cover letter",
                value=st.session_state["cover_letter"],
                height=380,
                label_visibility="collapsed"
            )
            st.download_button(
                "📥 Download Cover Letter",
                data=st.session_state["cover_letter"],
                file_name="cover_letter.txt",
                mime="text/plain",
            )

    # ── TAB 4: Interview Prep ────────────────────────────────────────────────
    with tab4:
        st.markdown("#### 🎯 Predicted Interview Questions")
        st.caption("Based on your resume gaps and the JD requirements.")
        if st.button("🎯 Generate Interview Questions", key="iq_btn"):
            with st.spinner("Predicting interview questions..."):
                st.session_state["questions"] = generate_interview_questions(
                    chunks, jd_text, analysis
                )
        if "questions" in st.session_state:
            type_badge = {
                "Technical":   "badge-blue",
                "Behavioural": "badge-orange",
                "Gap":         "badge-red",
            }
            for i, q in enumerate(st.session_state["questions"], 1):
                badge_style = type_badge.get(q["type"], "badge-purple")
                with st.expander(f"Q{i} — {q['question']}"):
                    render_badges([q["type"]], badge_style)
                    st.markdown(f"**💡 Tip:** {q['tip']}")

    # ── TAB 5: Bullet Rewriter ───────────────────────────────────────────────
    with tab5:
        st.markdown("#### ✏️ AI Resume Bullet Rewriter")
        st.caption("Paste your weak resume bullets — Gemini rewrites them to be stronger and ATS-optimized for this JD.")
        bullets_input = st.text_area(
            "Paste your resume bullets (one per line)",
            placeholder="• Built a machine learning model\n• Worked on data pipeline\n• Helped team with computer vision project",
            height=160,
        )
        if st.button("✨ Rewrite My Bullets", key="rw_btn"):
            if not bullets_input.strip():
                st.error("Please paste some resume bullets first.")
            else:
                with st.spinner("Rewriting bullets with Gemini..."):
                    st.session_state["rewrites"] = rewrite_bullets(
                        bullets_input, jd_text, chunks
                    )
        if "rewrites" in st.session_state:
            st.markdown("---")
            for item in st.session_state["rewrites"]:
                st.markdown(f'<div class="bullet-old">❌ <b>Before:</b> {item["original"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bullet-new">✅ <b>After:</b> {item["rewritten"]}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    # ── TAB 6: LinkedIn Summary ──────────────────────────────────────────────
    with tab6:
        st.markdown("#### 🔗 LinkedIn About Section Generator")
        st.caption("Generate a compelling LinkedIn summary based on your resume and target role.")
        if st.button("✨ Generate LinkedIn Summary", key="li_btn"):
            with st.spinner("Writing your LinkedIn summary..."):
                st.session_state["linkedin"] = generate_linkedin_summary(
                    chunks, jd_text, analysis
                )
        if "linkedin" in st.session_state:
            st.text_area(
                "Your LinkedIn summary",
                value=st.session_state["linkedin"],
                height=300,
                label_visibility="collapsed"
            )
            st.download_button(
                "📥 Download Summary",
                data=st.session_state["linkedin"],
                file_name="linkedin_summary.txt",
                mime="text/plain",
            )

    # ── TAB 7: Multi-JD Compare ──────────────────────────────────────────────
    with tab7:
        st.markdown("#### 🏆 Compare Multiple Job Descriptions")
        st.caption("Upload your resume once, paste up to 3 JDs — find out which role you're best suited for.")
        jd2 = st.text_area("Job Description 2", placeholder="Paste second JD here...", height=120, key="jd2")
        jd3 = st.text_area("Job Description 3 (optional)", placeholder="Paste third JD here...", height=120, key="jd3")

        if st.button("🏆 Compare All JDs", key="cmp_btn"):
            jds = [("JD 1 (original)", jd_text)]
            if jd2.strip(): jds.append(("JD 2", jd2))
            if jd3.strip(): jds.append(("JD 3", jd3))
            if len(jds) < 2:
                st.error("Please paste at least one more JD to compare.")
            else:
                with st.spinner(f"Comparing {len(jds)} job descriptions..."):
                    st.session_state["comparisons"] = compare_multiple_jds(
                        resume_text, jds
                    )

        if "comparisons" in st.session_state:
            comps = sorted(
                st.session_state["comparisons"],
                key=lambda x: x["match_score"],
                reverse=True
            )
            st.markdown("---")
            for rank, comp in enumerate(comps, 1):
                medal = ["🥇", "🥈", "🥉"][rank - 1]
                color, bg = score_color(comp["match_score"])
                with st.expander(f"{medal} Rank {rank} — {comp['jd_name']} — {comp['match_score']}% match"):
                    render_score_ring(comp["match_score"])
                    st.markdown(f"**Verdict:** {comp['verdict']}")
                    st.markdown("**Matched skills:**")
                    render_badges(comp["matched_skills"], "badge-green")
                    if comp["missing_skills"]:
                        st.markdown("**Missing skills:**")
                        render_badges(comp["missing_skills"], "badge-red")

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built by <b>Venu Enugula</b> ·
    <a href="https://github.com/Venuenugula" target="_blank">GitHub</a> ·
    Powered by Gemini 2.5 Flash + LangChain + FAISS + Streamlit
</div>
""", unsafe_allow_html=True)