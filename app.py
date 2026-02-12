import streamlit as st
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="AI Career Copilot", page_icon="🤖", layout="centered")

st.title("🤖 AI Career Copilot")
st.markdown("### Smart Resume Analyzer + ATS + JD Matcher")

role = st.selectbox(
    "🎯 Select your target job role:",
    ["Software Developer", "Data Scientist", "Cloud Engineer"]
)

uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])
jd_text = st.text_area("📋 Paste Job Description (Optional)")

def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def generate_pdf_report(score, ats_score, match_score, found_skills, missing_skills, feedback):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 11)

    lines = [
        "AI Career Copilot - Resume Analysis Report",
        "----------------------------------------",
        f"Resume Score: {score}/100",
        f"ATS Score: {ats_score}/100",
        f"JD Match Score: {match_score}%",
        "",
        "Skills Found:",
        ", ".join(found_skills) if found_skills else "None",
        "",
        "Missing Skills:",
        ", ".join(missing_skills),
        "",
        "AI Feedback:"
    ]

    for tip in feedback:
        lines.append(f"- {tip}")

    for line in lines:
        text.textLine(line)

    c.drawText(text)
    c.save()
    buffer.seek(0)
    return buffer

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)

    st.divider()
    st.subheader("📜 Resume Preview")
    st.write(text[:1200])

    # Role skills
    if role == "Software Developer":
        skills = ["Python", "Java", "C++", "SQL", "Git", "HTML", "CSS", "JavaScript"]
    elif role == "Data Scientist":
        skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]
    else:
        skills = ["AWS", "Cloud", "Linux", "Docker", "Python"]

    found_skills = [s for s in skills if s.lower() in text.lower()]
    missing_skills = [s for s in skills if s not in found_skills]

    st.divider()
    st.subheader("🧠 Resume Analysis")

    st.write("### ✅ Skills Found")
    st.write(found_skills if found_skills else "No matching skills")

    st.write("### ❌ Missing Skills")
    st.write(missing_skills)

    # Resume score
    score = int((len(found_skills) / len(skills)) * 100)
    st.divider()
    st.subheader("📊 Resume Strength Score")
    st.progress(score)
    st.write(f"{score}/100")

    # ATS score
    ats_score = 0
    if "skills" in text.lower(): ats_score += 20
    if "project" in text.lower(): ats_score += 20
    if "experience" in text.lower(): ats_score += 20
    if "education" in text.lower(): ats_score += 20
    if len(text.split()) > 200: ats_score += 20

    st.subheader("🤖 ATS Score")
    st.progress(ats_score)
    st.write(f"{ats_score}/100")

    # Feedback
    feedback = []

    if "experience" not in text.lower():
        feedback.append("Add an EXPERIENCE section.")
    if "project" not in text.lower():
        feedback.append("Add PROJECTS to show practical work.")
    if len(found_skills) < 3:
        feedback.append("Add more role-relevant SKILLS.")
    if len(text.split()) < 250:
        feedback.append("Resume content looks short.")
    if "certification" not in text.lower():
        feedback.append("Add certifications to stand out.")

    st.divider()
    st.subheader("🧠 AI Feedback")
    for tip in feedback:
        st.write("•", tip)

    # JD Match
    match_score = 0
    if jd_text:
        jd_words = jd_text.lower().split()
        resume_words = text.lower().split()
        common = set(jd_words).intersection(set(resume_words))
        if len(set(jd_words)) > 0:
            match_score = int((len(common) / len(set(jd_words))) * 100)

        st.divider()
        st.subheader("📊 JD Match Score")
        st.progress(match_score)
        st.write(f"{match_score}%")

    # PDF download
    st.divider()
    st.subheader("📥 Download Full Analysis Report")

    pdf_file = generate_pdf_report(
        score, ats_score, match_score, found_skills, missing_skills, feedback
    )

    st.download_button(
        label="Download Report as PDF",
        data=pdf_file,
        file_name="AI_Career_Copilot_Report.pdf",
        mime="application/pdf"
    )
