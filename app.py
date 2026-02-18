import streamlit as st
import re
from datetime import datetime

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="AI Career Copilot", layout="wide")

ADMIN_EMAIL = "copilotaicareer@gmail.com"
ADMIN_PASSWORD = "admin123"  # change later

# In-memory logs (reset on restart)
if "logs" not in st.session_state:
    st.session_state.logs = []

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# -------------------------------
# CLEAN UI HEADER
# -------------------------------
st.markdown("""
    <style>
    .main-title {
        font-size:34px;
        font-weight:700;
        color:#4CAF50;
    }
    .card {
        padding:18px;
        border-radius:12px;
        background:#f5f7fb;
        margin-bottom:10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 AI Career Copilot</div>', unsafe_allow_html=True)
st.caption("Upload Resume + Paste Job Description → Get ATS, Skills, Suggestions & Projects")

# -------------------------------
# ROLE → PROJECT DATABASE
# -------------------------------
PROJECT_DB = {
    "data scientist": {
        "Beginner": [
            "House Price Prediction using Linear Regression",
            "Titanic Survival Prediction"
        ],
        "Intermediate": [
            "Customer Churn Prediction",
            "Movie Recommendation System"
        ],
        "Strong": [
            "End-to-End ML Pipeline + Deployment",
            "Real-time Fraud Detection System"
        ],
    },
    "web developer": {
        "Beginner": [
            "Personal Portfolio Website",
            "To-Do App using HTML/CSS/JS"
        ],
        "Intermediate": [
            "Full Stack Blog App (React + Node)",
            "JWT Authentication System"
        ],
        "Strong": [
            "Scalable E-commerce Platform",
            "Microservices Web App"
        ],
    },
    "cloud engineer": {
        "Beginner": [
            "Deploy Static Website on AWS S3",
            "Linux Server Setup"
        ],
        "Intermediate": [
            "Auto-Scaling EC2 Project",
            "CI/CD Pipeline (GitHub Actions)"
        ],
        "Strong": [
            "Terraform Infrastructure Project",
            "Kubernetes Deployment"
        ],
    },
    "ai engineer": {
        "Beginner": [
            "Image Classifier using CNN",
            "Basic Chatbot"
        ],
        "Intermediate": [
            "Face Recognition Attendance System",
            "Resume Skill Extractor (NLP)"
        ],
        "Strong": [
            "LLM Career Assistant",
            "Deepfake Detection System"
        ],
    },
}

# -------------------------------
# SKILLS DB
# -------------------------------
COMMON_SKILLS = [
    "python","sql","aws","linux","docker","kubernetes",
    "machine learning","deep learning","react","node",
    "tensorflow","pandas","numpy","git"
]

# -------------------------------
# SIDEBAR → ADMIN LOGIN
# -------------------------------
st.sidebar.title("🔐 Admin Panel")

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        st.session_state.admin_logged_in = True
        st.sidebar.success("Logged in")
    else:
        st.sidebar.error("Invalid credentials")

# -------------------------------
# ADMIN DASHBOARD
# -------------------------------
if st.session_state.admin_logged_in:
    st.sidebar.markdown("---")
    if st.sidebar.button("Open Dashboard"):
        st.title("📊 Admin Dashboard")

        total_users = len(st.session_state.logs)

        st.metric("Total Resume Uploads", total_users)

        if total_users:
            st.subheader("Recent Activity")
            for log in reversed(st.session_state.logs[-10:]):
                st.write(log)

        st.stop()

# -------------------------------
# MAIN USER FEATURE
# -------------------------------
st.markdown("### 📄 Upload Resume")
resume = st.file_uploader("Upload Resume (TXT)", type=["txt"])

st.markdown("### 📋 Paste Job Description")
jd = st.text_area("Job Description")

if resume and jd:
    resume_text = resume.read().decode("utf-8").lower()
    jd_text = jd.lower()

    # ATS SCORE
    jd_words = set(jd_text.split())
    resume_words = set(resume_text.split())
    ats_score = int(len(jd_words & resume_words) / max(len(jd_words),1) * 100)

    # SKILLS MATCH
    matched = [s for s in COMMON_SKILLS if s in resume_text and s in jd_text]
    missing = [s for s in COMMON_SKILLS if s in jd_text and s not in resume_text]
    skill_score = int(len(matched) / (len(matched)+len(missing)+1) * 100)

    # ROLE DETECTION
    detected_role = None
    for role in PROJECT_DB:
        if role in jd_text:
            detected_role = role
            break

    # LEVEL COLOR
    if ats_score >= 75:
        level = "Strong"
        level_color = "green"
    elif ats_score >= 45:
        level = "Intermediate"
        level_color = "orange"
    else:
        level = "Beginner"
        level_color = "red"

    # SAVE LOG
    st.session_state.logs.append(
        f"{datetime.now().strftime('%d-%m %H:%M')} | ATS:{ats_score}% | Skill:{skill_score}%"
    )

    # -----------------------
    # SCORES UI
    # -----------------------
    st.markdown("## 📊 Analysis")

    c1, c2, c3 = st.columns(3)
    c1.metric("ATS Score", f"{ats_score}%")
    c2.metric("Skill Score", f"{skill_score}%")
    c3.markdown(f"**Level:** :{level_color}[{level}]")

    # -----------------------
    # SKILLS SECTION
    # -----------------------
    st.markdown("## 🧠 Skills Match")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✅ Skills Matched**")
        st.write(", ".join(matched) if matched else "No strong matches")

    with col2:
        st.markdown("**⚠ Skills Missing**")
        st.write(", ".join(missing) if missing else "No missing skills")

    # -----------------------
    # SUGGESTIONS
    # -----------------------
    st.markdown("## 💡 Suggestions")

    if missing:
        st.write("• Add missing skills to resume")
        st.write("• Build projects using missing skills")
        st.write("• Add certifications for role match")
    else:
        st.write("• Good profile — improve deployments & real-world projects")

    # -----------------------
    # PROJECTS
    # -----------------------
    st.markdown("## 🚀 Suggested Projects")

    if detected_role:
        st.info(f"Detected Role: {detected_role.title()}")

        for lvl, projects in PROJECT_DB[detected_role].items():
            if lvl == "Beginner":
                st.markdown("### 🟢 Beginner")
            elif lvl == "Intermediate":
                st.markdown("### 🟠 Intermediate")
            else:
                st.markdown("### 🔴 Strong Candidate")

            for p in projects:
                st.write("•", p)
    else:
        st.warning("Role not detected. Add role name in JD.")
