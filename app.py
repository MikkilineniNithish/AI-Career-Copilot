import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import PyPDF2
import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Career Copilot", layout="wide")

# ---------------- FIREBASE CONNECT ----------------
if not firebase_admin._apps:
    firebase_dict = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
    }

    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- PASSWORD HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- USER CREATE ----------------
def create_user(email, password):
    db.collection("users").document(email).set({
        "email": email,
        "password": hash_password(password)
    })

# ---------------- USER CHECK ----------------
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

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ---------------- LOGIN UI ----------------
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

    role = st.selectbox(
        "Select Target Role",
        ["Software Developer", "Data Scientist", "Cloud Engineer"]
    )

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    jd_text = st.text_area("Paste Job Description (Optional)")

    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)

        # ---------------- SKILLS ----------------
        if role == "Software Developer":
            skills = ["Python", "Java", "SQL", "Git", "HTML", "CSS", "JavaScript"]
        elif role == "Data Scientist":
            skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]
        else:
            skills = ["AWS", "Cloud", "Linux", "Docker", "Python"]

        found_skills = [s for s in skills if s.lower() in text.lower()]
        missing_skills = [s for s in skills if s not in found_skills]

        # ---------------- SCORES ----------------
        score = int((len(found_skills) / len(skills)) * 100)

        ats_score = 0
        if "skills" in text.lower(): ats_score += 20
        if "project" in text.lower(): ats_score += 20
        if "experience" in text.lower(): ats_score += 20
        if "education" in text.lower(): ats_score += 20
        if len(text.split()) > 200: ats_score += 20

        match_score = 0
        if jd_text:
            jd_words = jd_text.lower().split()
            resume_words = text.lower().split()
            common = set(jd_words).intersection(set(resume_words))
            if len(jd_words) > 0:
                match_score = int((len(common)/len(jd_words))*100)

        # ---------------- SAVE HISTORY ----------------
        db.collection("users") \
            .document(st.session_state.user_email) \
            .collection("history") \
            .add({
                "role": role,
                "skill_score": score,
                "ats_score": ats_score,
                "jd_score": match_score,
                "skills_found": found_skills,
                "skills_missing": missing_skills,
                "timestamp": datetime.datetime.utcnow()
            })

        st.success("Resume analyzed & saved!")

        # ---------------- DISPLAY ----------------
        st.subheader("📊 Resume Skill Score")
        st.progress(score)
        st.write(score)

        st.subheader("🤖 ATS Score")
        st.progress(ats_score)
        st.write(ats_score)

        if jd_text:
            st.subheader("🎯 JD Match Score")
            st.progress(match_score)
            st.write(match_score)

        # ---------------- RESUME STRENGTH LEVEL ----------------
        st.subheader("🏆 Resume Strength Level")

        average_score = score
        if jd_text:
            average_score = int((score + ats_score + match_score) / 3)
        else:
            average_score = int((score + ats_score) / 2)

        if average_score < 50:
            level = "🔴 Beginner Level"
        elif average_score < 75:
            level = "🟡 Intermediate Level"
        else:
            level = "🟢 Strong Candidate"

        st.metric("Overall Performance", f"{average_score}%")
        st.success(f"Current Level: {level}")

        st.subheader("✅ Skills Found")
        st.write(found_skills)

        st.subheader("❌ Missing Skills")
        st.write(missing_skills)
        # ---------------- AI LEARNING ROADMAP ----------------
        st.subheader("🧭 Personalized Learning Roadmap")

        roadmap = []
        
        if role == "Software Developer":
            roadmap = [
                "Step 1: Strengthen Programming (Python/Java)",
                "Step 2: Learn Data Structures & Algorithms",
                "Step 3: Build 3–5 Real Projects",
                "Step 4: Learn Git & System Design Basics",
                "Step 5: Start Applying for SDE Roles"
                ]
        elif role == "Data Scientist":
            roadmap = [
                "Step 1: Master Python & Pandas",
                "Step 2: Learn Statistics & Probability",
                "Step 3: Practice Machine Learning Models",
                "Step 4: Build Data Projects",
                "Step 5: Apply for Data Roles"
                ]
        elif role == "Cloud Engineer":
            roadmap = [
                "Step 1: Learn Linux Basics",
                "Step 2: Learn AWS Core Services",
                "Step 3: Practice Docker & Deployment",
                "Step 4: Build Cloud Projects",
                "Step 5: Get AWS Certification"
                ]
            for step in roadmap:
                st.write("•", step)

        # ---------------- CAREER SUGGESTIONS ----------------
        st.subheader("🤖 Career Suggestions")

        if missing_skills:
            suggestion_text = f"""
To improve your profile for the role of {role}, focus on learning:
{', '.join(missing_skills)}.

Build projects using these skills and update your resume.
"""
        else:
            suggestion_text = "Great! Your resume already matches the role well."

        st.info(suggestion_text)

        # ---------------- PROJECT SUGGESTIONS ----------------
        st.subheader("🚀 Suggested Projects To Build")

        project_map = {
            "Python": [
                "Student Management System using Python",
                "AI Chatbot using Python",
                "Automation Script for File Organizer"
            ],
            "SQL": [
                "Library Database Management System",
                "E-commerce Backend using SQL"
            ],
            "Java": [
                "Online Banking Application",
                "Spring Boot REST API Project"
            ],
            "AWS": [
                "Deploy Website using EC2 + S3",
                "Serverless App using Lambda"
            ],
            "Docker": [
                "Containerize Flask Application",
                "Dockerize Node.js Project"
            ],
            "Machine Learning": [
                "House Price Prediction Model",
                "Spam Email Classifier"
            ],
            "Pandas": [
                "Data Analysis Dashboard",
                "Sales Data Insights Project"
            ],
            "Linux": [
                "Shell Script Automation Tool",
                "Log Monitoring System"
            ]
        }

        suggested_projects = []
        for skill in missing_skills:
            if skill in project_map:
                suggested_projects.extend(project_map[skill])

        if suggested_projects:
            for proj in suggested_projects[:6]:
                st.write("•", proj)
        else:
            st.write("🔥 Your skill set is strong. Start applying for jobs!")

    # ---------------- HISTORY DASHBOARD ----------------
    st.divider()
    st.subheader("📈 Past Analysis History")

    history_docs = db.collection("users") \
        .document(st.session_state.user_email) \
        .collection("history") \
        .stream()

    for doc in history_docs:
        data = doc.to_dict()
        st.write("Role:", data["role"])
        st.write("Skill Score:", data["skill_score"])
        st.write("ATS Score:", data["ats_score"])
        st.write("JD Score:", data["jd_score"])
        st.write("Time:", data["timestamp"])
        st.write("---")
