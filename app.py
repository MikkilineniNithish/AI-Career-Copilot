import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import PyPDF2

st.set_page_config(page_title="AI Career Copilot", layout="wide")

# ---------------- FIREBASE ----------------
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

# ---------------- FUNCTIONS ----------------
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

def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    st.title("🚀 AI Career Copilot")
    choice = st.radio("Choose", ["Login", "Signup"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            create_user(email, password)
            st.success("Account created!")

    if choice == "Login":
        if st.button("Login"):
            if check_user(email, password):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------------- MAIN ----------------
else:

    st.sidebar.success("Logged in")
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
        text = extract_text(uploaded_file)

        st.success("Resume saved successfully!")

        if role == "Software Developer":
            skills = ["Python", "Java", "SQL", "Git", "HTML", "CSS", "JavaScript"]
        elif role == "Data Scientist":
            skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]
        else:
            skills = ["AWS", "Linux", "Docker", "Cloud", "Python"]

        found = [s for s in skills if s.lower() in text.lower()]
        missing = [s for s in skills if s not in found]

        resume_score = int((len(found)/len(skills))*100)

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

        st.subheader("📊 Resume Skill Score")
        st.progress(resume_score)

        st.subheader("🤖 ATS Score")
        st.progress(ats_score)

        if jd_text:
            st.subheader("🎯 JD Match Score")
            st.progress(match_score)

        st.subheader("✅ Skills Found")
        st.write(found)

        st.subheader("❌ Missing Skills")
        st.write(missing)

