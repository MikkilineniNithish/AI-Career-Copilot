import streamlit as st
from datetime import datetime
import PyPDF2
import docx
import re

st.set_page_config(page_title="AI Career Copilot", layout="wide")

# -------------------------
# ADMIN SETTINGS
# -------------------------
ADMIN_EMAIL = "copilotaicareer@gmail.com"

if "logs" not in st.session_state:
    st.session_state.logs = []

# -------------------------
# SKILLS DATABASE
# -------------------------
COMMON_SKILLS = [
    "python","sql","aws","linux","docker","kubernetes",
    "machine learning","deep learning","react","node",
    "tensorflow","pandas","numpy","git","html","css","javascript"
]

# -------------------------
# PROJECT DATABASE
# -------------------------
PROJECT_DB = {
    "data scientist": {
        "Beginner": ["House Price Prediction","Titanic ML Project"],
        "Intermediate": ["Customer Churn Prediction","Movie Recommendation System"],
        "Strong": ["End-to-End ML Deployment","Real-time Fraud Detection"],
    },
    "web developer": {
        "Beginner": ["Portfolio Website","To-Do App"],
        "Intermediate": ["Full Stack Blog App","JWT Authentication System"],
        "Strong": ["E-commerce Platform","Microservices Web App"],
    },
    "cloud engineer": {
        "Beginner": ["Deploy Website on AWS S3","Linux Server Setup"],
        "Intermediate": ["Auto Scaling EC2 Project","CI/CD Pipeline"],
        "Strong": ["Terraform Infra Project","Kubernetes Deployment"],
    },
    "ai engineer": {
        "Beginner": ["Image Classifier","Basic Chatbot"],
        "Intermediate": ["Face Recognition System","Resume Skill Extractor"],
        "Strong": ["LLM Career Assistant","Deepfake Detection System"],
    },
}

# -------------------------
# TEXT EXTRACTOR (STRONGER)
# -------------------------
def extract_text(file):
    text = ""
    try:
        if file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content + " "

        elif file.name.endswith(".docx"):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + " "

        elif file.name.endswith(".txt"):
            text = file.read().decode("utf-8")

    except:
        return ""

    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    return text.lower()

# -------------------------
# HEADER
# -------------------------
st.markdown("""
<style>
.title {font-size:34px;font-weight:700;color:#4CAF50;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 AI Career Copilot</div>', unsafe_allow_html=True)
st.caption("Upload Resume + Paste JD → ATS + Skills + Suggestions + Projects")

# -------------------------
# ADMIN PANEL
# -------------------------
st.sidebar.title("Admin Access")
admin_email_input = st.sidebar.text_input("Enter Admin Email")

if st.sidebar.button("Open Admin Dashboard"):
    if admin_email_input == ADMIN_EMAIL:
        st.title("📊 Admin Dashboard")
        st.metric("Total Resume Uploads", len(st.session_state.logs))
        st.subheader("Recent Activity")
        for log in reversed(st.session_state.logs[-10:]):
            st.write(log)
        st.stop()
    else:
        st.sidebar.error("Not authorized")

# -------------------------
# USER AREA
# -------------------------
st.markdown("### 📄 Upload Resume")
resume = st.file_uploader("Upload Resume", type=["pdf","docx","txt"])

st.markdown("### 📋 Paste Job Description")
jd = st.text_area("Paste JD here")

analyze = st.button("🔍 Analyze")

# -------------------------
# ANALYSIS
# -------------------------
if analyze:
    if not resume:
        st.error("Upload resume")
        st.stop()

    if not jd:
        st.error("Paste JD")
        st.stop()

    resume_text = extract_text(resume)
    jd_text = jd.lower()

    if resume_text == "":
        st.error("Could not read resume. Try DOCX/TXT for best results.")
        st.stop()

    # ATS
    jd_words = set(jd_text.split())
    resume_words = set(resume_text.split())
    ats_score = int(len(jd_words & resume_words) / max(len(jd_words),1) * 100)

    # SKILLS
    matched = [s for s in COMMON_SKILLS if s in resume_text]
    missing = [s for s in COMMON_SKILLS if s in jd_text and s not in resume_text]
    skill_score = int(len(matched) / len(COMMON_SKILLS) * 100)

    # AUTO ROLE DETECTION (NEW)
    if any(x in resume_text for x in ["aws","docker","kubernetes","linux"]):
        detected_role = "cloud engineer"
    elif any(x in resume_text for x in ["react","html","css","javascript"]):
        detected_role = "web developer"
    elif any(x in resume_text for x in ["machine learning","tensorflow","deep learning"]):
        detected_role = "ai engineer"
    elif any(x in resume_text for x in ["pandas","numpy","sql"]):
        detected_role = "data scientist"
    else:
        detected_role = "data scientist"

    # LEVEL
    if ats_score >= 75:
        level = "Strong"
        color="green"
    elif ats_score >= 45:
        level = "Intermediate"
        color="orange"
    else:
        level = "Beginner"
        color="red"

    st.session_state.logs.append(
        f"{datetime.now().strftime('%d-%m %H:%M')} | ATS:{ats_score}% | Skill:{skill_score}%"
    )

    # SCORES
    st.markdown("## 📊 Analysis")
    c1,c2,c3=st.columns(3)
    c1.metric("ATS Score",f"{ats_score}%")
    c2.metric("Skill Score",f"{skill_score}%")
    c3.markdown(f"**Level:** :{color}[{level}]")

    # SKILLS
    st.markdown("## 🧠 Skills Match")
    col1,col2=st.columns(2)

    with col1:
        st.markdown("### ✅ Skills Found")
        st.write(", ".join(matched[:12]))

    with col2:
        st.markdown("### ⚠ Skills Missing")
        st.write(", ".join(missing[:12]) if missing else "No missing skills")

    # SUGGESTIONS
    st.markdown("## 💡 Suggestions")
    if missing:
        st.write("• Add missing skills to resume")
        st.write("• Add projects using missing skills")
    else:
        st.write("• Strong profile — focus on deployment projects")

    # PROJECTS
    st.markdown("## 🚀 Suggested Projects")
    st.info(f"Detected Role: {detected_role.title()}")

    for lvl,projects in PROJECT_DB[detected_role].items():
        st.markdown(f"### {lvl}")
        for p in projects:
            st.write("•",p)
