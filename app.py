import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Career Copilot", layout="wide")

# -----------------------------
# FIREBASE CONNECTION
# -----------------------------
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

# -----------------------------
# HELPERS
# -----------------------------
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

# -----------------------------
# ATS ANALYSIS LOGIC
# -----------------------------
skills_db = [
    "python","java","c++","sql","machine learning","deep learning",
    "html","css","javascript","react","node","aws","docker",
    "kubernetes","data science","ai","nlp","pandas","numpy"
]

def analyze_resume(text):
    text_lower = text.lower()

    found_skills = [skill for skill in skills_db if skill in text_lower]

    score = min(100, len(found_skills) * 5 + 30)

    suggestions = []
    if "project" not in text_lower:
        suggestions.append("Add projects section")
    if "experience" not in text_lower:
        suggestions.append("Add experience section")
    if "skills" not in text_lower:
        suggestions.append("Add skills section")

    return score, found_skills, suggestions

# -----------------------------
# SESSION
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# -----------------------------
# LOGIN UI
# -----------------------------
if not st.session_state.logged_in:

    st.title("🚀 AI Career Copilot")
    st.subheader("Login / Signup")

    choice = st.radio("Choose", ["Login", "Signup"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            if email and password:
                create_user(email, password)
                st.success("Account created! Now login.")
            else:
                st.error("Enter all details")

    else:
        if st.button("Login"):
            if check_user(email, password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Invalid credentials")

# -----------------------------
# MAIN APP
# -----------------------------
else:
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🎯 AI Career Copilot")
    st.write("Upload your resume and get instant ATS analysis")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file:
        resume_text = uploaded_file.read().decode(errors="ignore")

        # Save to Firebase
        db.collection("resumes").document(st.session_state.user_email).set({
            "resume_text": resume_text
        })

        st.success("Resume saved successfully!")

        # ANALYSIS
        score, skills, suggestions = analyze_resume(resume_text)

        st.header("📊 ATS Score")
        st.progress(score)
        st.write(f"Score: {score}/100")

        st.header("🧠 Skills Detected")
        if skills:
            for s in skills:
                st.write("✔", s)
        else:
            st.write("No major skills detected")

        st.header("📌 Suggestions")
        if suggestions:
            for s in suggestions:
                st.write("•", s)
        else:
            st.write("Great resume structure!")
