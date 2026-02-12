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

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Career Copilot",
    page_icon="🤖",
    layout="centered"
)

# ---------------- LOGIN SYSTEM ----------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_signup():
    st.sidebar.title("🔐 Account Access")

    option = st.sidebar.radio("Choose Option", ["Login", "Signup"])

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if option == "Signup":
        if st.sidebar.button("Create Account"):
            if email in st.session_state.users:
                st.sidebar.error("User already exists")
            else:
                st.session_state.users[email] = password
                st.sidebar.success("Account created! Please login.")

    if option == "Login":
        if st.sidebar.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.sidebar.success("Login successful!")
            else:
                st.sidebar.error("Invalid email or password")

login_signup()

# Stop app if not logged in
if not st.session_state.logged_in:
    st.title("🤖 AI Career Copilot")
    st.info("Please login or signup from the left sidebar to continue.")
    st.stop()

# ---------------- MAIN APP ----------------
st.title("🤖 AI Career Copilot")
st.markdown("### Smart Resume Analyzer + ATS + JD Matcher")
st.success(f"Logged in as: {st.session_state.user_email}")

role = st.selectbox(
    "🎯 Select your target job role:",
    ["Software Developer", "Data Scientist", "Cloud Engineer"]
)

uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])
jd_text = st.text_area("📋 Paste Job Description (Optional)")

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


def generate_pdf_report(score, ats_score, match_score, found_skills, missing_skills, feedback):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AI Career Copilot - Resume Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Scores Overview", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Resume Strength Score:</b> {score}/100", styles["Normal"]))
    elements.append(Paragraph(f"<b>ATS Compatibility Score:</b> {ats_score}/100", styles["Normal"]))
    elements.append(Paragraph(f"<b>JD Match Score:</b> {match_score}%", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Skills Found", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    if found_skills:
        skill_list = [ListItem(Paragraph(skill, styles["Normal"])) for skill in found_skills]
        elements.append(ListFlowable(skill_list, bulletType="bullet"))
    else:
        elements.append(Paragraph("No matching skills detected.", styles["Normal"]))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Recommended Skills to Add", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    if missing_skills:
        missing_list = [ListItem(Paragraph(skill, styles["Normal"])) for skill in missing_skills]
        elements.append(ListFlowable(missing_list, bulletType="bullet"))
    else:
        elements.append(Paragraph("No major skill gaps detected.", styles["Normal"]))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("AI Career Feedback", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    if feedback:
        feedback_list = [ListItem(Paragraph(tip, styles["Normal"])) for tip in feedback]
        elements.append(ListFlowable(feedback_list, bulletType="bullet"))
    else:
        elements.append(Paragraph("Your resume structure looks strong.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ---------------- ANALYSIS ----------------
if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)

    st.divider()
    st.subheader("📜 Resume Preview")
    st.write(text[:1200])

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

    score = int((len(found_skills) / len(skills)) * 100)

    st.divider()
    st.subheader("📊 Resume Strength Score")
    st.progress(score)
    st.write(f"{score}/100")

    ats_score = 0
    if "skills" in text.lower(): ats_score += 20
    if "project" in text.lower(): ats_score += 20
    if "experience" in text.lower(): ats_score += 20
    if "education" in text.lower(): ats_score += 20
    if len(text.split()) > 200: ats_score += 20

    st.subheader("🤖 ATS Compatibility Score")
    st.progress(ats_score)
    st.write(f"{ats_score}/100")

    feedback = []
    if "experience" not in text.lower():
        feedback.append("Add an EXPERIENCE section.")
    if "project" not in text.lower():
        feedback.append("Include PROJECTS to show practical exposure.")
    if len(found_skills) < 3:
        feedback.append("Add more role-relevant SKILLS.")
    if len(text.split()) < 250:
        feedback.append("Resume content appears short.")
    if "certification" not in text.lower():
        feedback.append("Add certifications to strengthen your profile.")

    st.divider()
    st.subheader("🧠 AI Career Feedback")
    for tip in feedback:
        st.write("•", tip)

    match_score = 0
    if jd_text:
        jd_words = jd_text.lower().split()
        resume_words = text.lower().split()
        common = set(jd_words).intersection(set(resume_words))

        if len(set(jd_words)) > 0:
            match_score = int((len(common) / len(set(jd_words))) * 100)

        st.divider()
        st.subheader("📊 Resume vs Job Description Match Score")
        st.progress(match_score)
        st.write(f"{match_score}%")

    st.divider()
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
