import streamlit as st
import PyPDF2
import io

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Career Copilot",
    page_icon="🤖",
    layout="centered"
)

# ---------- DARK UI ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f172a,#020617);
    color: white;
}

h1, h2, h3 {
    color: #38bdf8;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background: rgba(255,255,255,0.04);
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("🤖 AI Career Copilot")
st.markdown("### 🚀 Smart Resume Analyzer + ATS + JD Matcher")

role = st.selectbox(
    "🎯 Select your target job role:",
    ["Software Developer", "Data Scientist", "Cloud Engineer"]
)

uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])
jd_text = st.text_area("📋 Paste Job Description (Optional)")


# ---------- PDF TEXT EXTRACT ----------
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


# ---------- PDF REPORT ----------
def generate_pdf_report(score, ats_score, match_score, found_skills, missing_skills, feedback):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AI Career Copilot - Resume Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Scores Overview", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Resume Score:</b> {score}/100", styles["Normal"]))
    elements.append(Paragraph(f"<b>ATS Score:</b> {ats_score}/100", styles["Normal"]))
    elements.append(Paragraph(f"<b>JD Match Score:</b> {match_score}%", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Skills Found", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    skill_list = [ListItem(Paragraph(skill, styles["Normal"])) for skill in found_skills]
    elements.append(ListFlowable(skill_list, bulletType="bullet"))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Missing Skills", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    missing_list = [ListItem(Paragraph(skill, styles["Normal"])) for skill in missing_skills]
    elements.append(ListFlowable(missing_list, bulletType="bullet"))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("AI Career Feedback", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    feedback_list = [ListItem(Paragraph(tip, styles["Normal"])) for tip in feedback]
    elements.append(ListFlowable(feedback_list, bulletType="bullet"))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ---------- MAIN ----------
if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📜 Resume Preview")
    st.write(text[:1000])
    st.markdown('</div>', unsafe_allow_html=True)

    # Role skills
    if role == "Software Developer":
        skills = ["Python", "Java", "C++", "SQL", "Git", "HTML", "CSS", "JavaScript"]
    elif role == "Data Scientist":
        skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]
    else:
        skills = ["AWS", "Cloud", "Linux", "Docker", "Python"]

    found_skills = [s for s in skills if s.lower() in text.lower()]
    missing_skills = [s for s in skills if s not in found_skills]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧠 Resume Analysis")

    st.write("### ✅ Skills Found")
    st.write(found_skills if found_skills else "No matching skills")

    st.write("### ❌ Missing Skills")
    st.write(missing_skills)
    st.markdown('</div>', unsafe_allow_html=True)

    # Resume Score
    score = int((len(found_skills) / len(skills)) * 100)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Resume Strength Score")
    st.progress(score)
    st.write(f"{score}/100")
    st.markdown('</div>', unsafe_allow_html=True)

    # ATS Score
    ats_score = 0
    if "skills" in text.lower(): ats_score += 20
    if "project" in text.lower(): ats_score += 20
    if "experience" in text.lower(): ats_score += 20
    if "education" in text.lower(): ats_score += 20
    if len(text.split()) > 200: ats_score += 20

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 ATS Compatibility Score")
    st.progress(ats_score)
    st.write(f"{ats_score}/100")
    st.markdown('</div>', unsafe_allow_html=True)

    # AI Feedback
    feedback = []
    if "experience" not in text.lower():
        feedback.append("Add an EXPERIENCE section")
    if "project" not in text.lower():
        feedback.append("Include PROJECTS")
    if len(found_skills) < 3:
        feedback.append("Add more relevant SKILLS")
    if len(text.split()) < 250:
        feedback.append("Resume content is short")
    if "certification" not in text.lower():
        feedback.append("Add CERTIFICATIONS")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧠 AI Career Feedback")
    for tip in feedback:
        st.write("•", tip)
    st.markdown('</div>', unsafe_allow_html=True)

    # JD Match
    match_score = 0
    if jd_text:
        jd_words = jd_text.lower().split()
        resume_words = text.lower().split()
        common = set(jd_words).intersection(set(resume_words))

        if len(set(jd_words)) > 0:
            match_score = int((len(common) / len(set(jd_words))) * 100)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 JD Match Score")
        st.progress(match_score)
        st.write(f"{match_score}%")
        st.markdown('</div>', unsafe_allow_html=True)

    # PDF Download
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📥 Download Full Analysis Report")

    pdf_file = generate_pdf_report(
        score,
        ats_score,
        match_score,
        found_skills,
        missing_skills,
        feedback
    )

    st.download_button(
        label="Download Report as PDF",
        data=pdf_file,
        file_name="AI_Career_Copilot_Report.pdf",
        mime="application/pdf"
    )
    st.markdown('</div>', unsafe_allow_html=True)
