import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import PyPDF2
from fpdf import FPDF

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Career Copilot", layout="wide")

# ---------------- FIREBASE CONNECT ----------------
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- PASSWORD HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    db.collection("users").document(email).set({
        "email": email,
        "password": hash_password(password)
    })

def check_user(email, password):
    user_doc = db.collection("users").document(email).get()
    if user_doc.exists:
        return user_doc.to_dict()["password"] == hash_password(password)
    return False

# ---------------- PDF TEXT EXTRACT ----------------
def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

# ---------------- CREATE PDF REPORT ----------------
def generate_pdf(role, score, ats_score, match_score, level, roadmap, projects):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AI Career Copilot Report", ln=True, align="C")
    pdf.ln(5)

    pdf.cell(200, 10, txt=f"Role: {role}", ln=True)
    pdf.cell(200, 10, txt=f"Skill Score: {score}%", ln=True)
    pdf.cell(200, 10, txt=f"ATS Score: {ats_score}%", ln=True)
    pdf.cell(200, 10, txt=f"JD Match Score: {match_score}%", ln=True)
    pdf.cell(200, 10, txt=f"Level: {level}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Learning Roadmap:", ln=True)
    for step in roadmap:
        pdf.multi_cell(0, 8, txt=f"- {step}")

    pdf.ln(5)
    pdf.cell(200, 10, txt="Suggested Projects:", ln=True)
    for proj in projects:
        pdf.multi_cell(0, 8, txt=f"- {proj}")

    return pdf.output(dest="S").encode("latin-1")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    st.title("🚀 AI Career Copilot")
    st.subheader("Login / Signup")

    choice = st.radio("Choose", ["Login", "Signup"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            create_user(email, password)
            st.success("Account created! Now login.")

    if choice == "Login":
        if st.button("Login"):
            if check_user(email, password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------------- MAIN APP ----------------
else:

    st.sidebar.success(f"Logged in as {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🤖 AI Career Copilot")
    st.caption("Your personal AI career growth assistant")

    role = st.selectbox(
        "🎯 Select Target Role",
        ["Software Developer", "Data Scientist", "Cloud Engineer"]
    )

    uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf"])
    jd_text = st.text_area("Paste Job Description (Optional)")

    if uploaded_file:

        text = extract_text_from_pdf(uploaded_file)

        # ---------------- SKILLS ----------------
        role_skills = {
            "Software Developer": ["Python", "Java", "SQL", "Git", "HTML", "CSS", "JavaScript"],
            "Data Scientist": ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"],
            "Cloud Engineer": ["AWS", "Cloud", "Linux", "Docker", "Python"]
        }

        skills = role_skills[role]
        found_skills = [s for s in skills if s.lower() in text.lower()]
        missing_skills = [s for s in skills if s not in found_skills]

        score = int((len(found_skills) / len(skills)) * 100)

        # ---------------- ATS SCORE ----------------
        ats_score = 0
        for word in ["skills", "project", "experience", "education"]:
            if word in text.lower():
                ats_score += 20
        if len(text.split()) > 200:
            ats_score += 20

        # ---------------- JD MATCH ----------------
        match_score = 0
        if jd_text:
            jd_words = set(jd_text.lower().split())
            resume_words = set(text.lower().split())
            if len(jd_words) > 0:
                match_score = int((len(jd_words.intersection(resume_words)) / len(jd_words)) * 100)

        # ---------------- SCORES UI ----------------
        st.subheader("📊 Resume Analysis")

        col1, col2, col3 = st.columns(3)
        col1.metric("Skill Score", f"{score}%")
        col2.metric("ATS Score", f"{ats_score}%")
        col3.metric("JD Match", f"{match_score}%")

        # ---------------- LEVEL ----------------
        avg = (score + ats_score + match_score) / 3 if jd_text else (score + ats_score) / 2

        if avg < 50:
            level = "Beginner"
            st.error("🔴 Beginner Level")
        elif avg < 75:
            level = "Intermediate"
            st.warning("🟡 Intermediate Level")
        else:
            level = "Strong Candidate"
            st.success("🟢 Strong Candidate")

        # ---------------- ROADMAP ----------------
        st.subheader("🧭 Personalized Learning Roadmap")

        roadmap_map = {
            "Software Developer": [
                "Master DSA",
                "Build 5 Full Stack Projects",
                "Learn System Design",
                "Practice Coding Interviews"
            ],
            "Data Scientist": [
                "Advanced Machine Learning",
                "Deep Learning Projects",
                "Deploy ML Models",
                "Build Portfolio"
            ],
            "Cloud Engineer": [
                "Master AWS Core Services",
                "Learn CI/CD Pipelines",
                "Deploy Real Apps",
                "Get AWS Certification"
            ]
        }

        roadmap = roadmap_map[role]
        for step in roadmap:
            st.write("•", step)

        # ---------------- PROJECT SUGGESTIONS (ALWAYS SHOW) ----------------
        st.subheader("🚀 Suggested Projects")

        learning_projects = [
            "Resume Analyzer using Python",
            "Portfolio Website",
            "Automation Script",
            "REST API Project"
        ]

        advanced_projects = {
            "Software Developer": [
                "Full Stack E-commerce Platform",
                "Microservices App",
                "Real-time Chat Application"
            ],
            "Data Scientist": [
                "End-to-End ML Pipeline",
                "Stock Price Predictor",
                "AI Recommendation System"
            ],
            "Cloud Engineer": [
                "AWS 3-Tier Architecture",
                "Serverless App with Lambda",
                "CI/CD Deployment Pipeline"
            ]
        }

        if missing_skills:
            suggested_projects = learning_projects
        else:
            suggested_projects = advanced_projects[role]

        for proj in suggested_projects:
            st.write("•", proj)

        # ---------------- PDF DOWNLOAD ----------------
        st.subheader("📄 Download PDF Report")

        pdf_data = generate_pdf(role, score, ats_score, match_score, level, roadmap, suggested_projects)

        st.download_button(
            label="Download Career Report",
            data=pdf_data,
            file_name="career_report.pdf",
            mime="application/pdf"
        )
