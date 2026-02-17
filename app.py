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
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- PASSWORD HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- USER CREATE ----------------
def create_user(email, password):
    user_ref = db.collection("users").document(email)
    if user_ref.get().exists:
        return False
    user_ref.set({
        "email": email,
        "password": hash_password(password)
    })
    return True

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
            if create_user(email, password):
                st.success("Account created! Now login.")
            else:
                st.warning("User already exists.")

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

        score = int((len(found_skills) / len(skills)) * 100)

        # ---------------- ATS SCORE ----------------
        ats_score = 0
        keywords = ["skills", "project", "experience", "education"]
        for word in keywords:
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

        # ---------------- SAVE HISTORY ----------------
        db.collection("users") \
            .document(st.session_state.user_email) \
            .collection("history") \
            .add({
                "role": role,
                "skill_score": score,
                "ats_score": ats_score,
                "jd_score": match_score,
                "timestamp": datetime.datetime.utcnow()
            })

        st.success("Resume analyzed & saved!")

        # ---------------- DISPLAY SCORES ----------------
        st.subheader("📊 Resume Skill Score")
        st.progress(score)
        st.write(f"{score}%")

        st.subheader("🤖 ATS Score")
        st.progress(ats_score)
        st.write(f"{ats_score}%")

        if jd_text:
            st.subheader("🎯 JD Match Score")
            st.progress(match_score)
            st.write(f"{match_score}%")

        # ---------------- OVERALL LEVEL ----------------
        if jd_text:
            average_score = int((score + ats_score + match_score) / 3)
        else:
            average_score = int((score + ats_score) / 2)

        st.subheader("🏆 Resume Strength Level")
        st.metric("Overall Performance", f"{average_score}%")

        if average_score < 50:
            st.error("🔴 Beginner Level")
        elif average_score < 75:
            st.warning("🟡 Intermediate Level")
        else:
            st.success("🟢 Strong Candidate")

        # ---------------- SKILLS DISPLAY ----------------
        st.subheader("✅ Skills Found")
        st.write(found_skills)

        st.subheader("❌ Missing Skills")
        st.write(missing_skills)

        # ---------------- FIXED ROADMAP ----------------
        st.subheader("🧭 Personalized Learning Roadmap")

        if role == "Software Developer":
            roadmap = [
                "Strengthen Programming (Python/Java)",
                "Learn DSA",
                "Build 3–5 Real Projects",
                "Learn Git & System Design Basics",
                "Start Applying for SDE Roles"
            ]
        elif role == "Data Scientist":
            roadmap = [
                "Master Python & Pandas",
                "Learn Statistics",
                "Practice ML Models",
                "Build Data Projects",
                "Apply for Data Roles"
            ]
        else:
            roadmap = [
                "Learn Linux Basics",
                "Learn AWS Core Services",
                "Practice Docker",
                "Build Cloud Projects",
                "Get AWS Certification"
            ]

        for step in roadmap:
            st.write("•", step)

    # ---------------- HISTORY ----------------
    st.divider()
    st.subheader("📈 Past Analysis History")

    history_docs = db.collection("users") \
        .document(st.session_state.user_email) \
        .collection("history") \
        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
        .stream()

    for doc in history_docs:
        data = doc.to_dict()
        st.write(f"Role: {data['role']}")
        st.write(f"Skill Score: {data['skill_score']}%")
        st.write(f"ATS Score: {data['ats_score']}%")
        st.write(f"JD Score: {data['jd_score']}%")
        st.write(f"Time: {data['timestamp']}")
        st.write("---")
