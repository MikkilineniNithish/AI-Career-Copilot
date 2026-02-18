import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import PyPDF2
import datetime
from fpdf import FPDF

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Career Copilot", layout="wide")

# ---------------- CUSTOM UI STYLE ----------------
st.markdown("""
    <style>
    .main-title {
        font-size:40px;
        font-weight:700;
        background: linear-gradient(to right, #4e73df, #1cc88a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .card {
        padding:20px;
        border-radius:15px;
        background-color:#f8f9fc;
        box-shadow:0 4px 8px rgba(0,0,0,0.05);
        margin-bottom:20px;
    }
    </style>
""", unsafe_allow_html=True)

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

# ---------------- ADMIN CONFIG ----------------
ADMIN_EMAIL = "copilotaicareer@gmail.com"
ADMIN_PASSWORD = "admin123"

# ---------------- PASSWORD HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- USER FUNCTIONS ----------------
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

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# ---------------- LOGIN UI ----------------
if not st.session_state.logged_in:

    st.markdown('<div class="main-title">🚀 AI Career Copilot</div>', unsafe_allow_html=True)
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

    if st.sidebar.button("Admin Dashboard"):
        st.session_state.admin_mode = True

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- ADMIN DASHBOARD ----------------
    if st.session_state.admin_mode:

        st.title("📊 Admin Analytics Dashboard")

        users = list(db.collection("users").stream())
        total_users = len(users)

        total_resumes = 0
        total_skill = 0
        total_ats = 0
        total_jd = 0
        strong = 0
        intermediate = 0
        beginner = 0

        for user in users:
            history = db.collection("users").document(user.id).collection("history").stream()
            for record in history:
                data = record.to_dict()
                total_resumes += 1
                total_skill += data.get("skill_score", 0)
                total_ats += data.get("ats_score", 0)
                total_jd += data.get("jd_score", 0)

                avg = (data.get("skill_score",0) + data.get("ats_score",0) + data.get("jd_score",0)) / 3

                if avg < 50:
                    beginner += 1
                elif avg < 75:
                    intermediate += 1
                else:
                    strong += 1

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total Users", total_users)
        col2.metric("📄 Total Resume Analyses", total_resumes)
        col3.metric("🏆 Strong Profiles", strong)

        if total_resumes > 0:
            st.metric("📊 Avg Skill Score", int(total_skill/total_resumes))
            st.metric("🤖 Avg ATS Score", int(total_ats/total_resumes))
            st.metric("🎯 Avg JD Score", int(total_jd/total_resumes))

        st.subheader("Profile Distribution")
        st.write("🔴 Beginner:", beginner)
        st.write("🟡 Intermediate:", intermediate)
        st.write("🟢 Strong:", strong)

        if st.button("Exit Admin"):
            st.session_state.admin_mode = False
            st.rerun()

    # ---------------- USER APP ----------------
    else:

        st.markdown('<div class="main-title">🤖 AI Career Copilot</div>', unsafe_allow_html=True)

        role = st.selectbox(
            "Select Target Role",
            ["Software Developer", "Data Scientist", "Cloud Engineer"]
        )

        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        jd_text = st.text_area("Paste Job Description (Optional)")

        if uploaded_file:
            text = extract_text_from_pdf(uploaded_file)

            if role == "Software Developer":
                skills = ["Python", "Java", "SQL", "Git", "HTML", "CSS", "JavaScript"]
            elif role == "Data Scientist":
                skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]
            else:
                skills = ["AWS", "Cloud", "Linux", "Docker", "Python"]

            found_skills = [s for s in skills if s.lower() in text.lower()]
            missing_skills = [s for s in skills if s not in found_skills]

            score = int((len(found_skills)/len(skills))*100)

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

            st.subheader("📊 Performance Overview")
            col1, col2, col3 = st.columns(3)
            col1.metric("Skill Score", f"{score}%")
            col2.metric("ATS Score", f"{ats_score}%")
            col3.metric("JD Match", f"{match_score}%")

            avg = (score + ats_score + match_score) / 3
            if avg < 50:
                st.error("🔴 Beginner Profile")
            elif avg < 75:
                st.warning("🟡 Intermediate Profile")
            else:
                st.success("🟢 Strong Candidate")

            st.subheader("🚀 Suggested Projects")

            role_projects = {
                "Software Developer": [
                    "Full Stack Web App",
                    "Real-time Chat App",
                    "Task Manager API",
                    "Code Editor Platform"
                ],
                "Data Scientist": [
                    "Stock Prediction Dashboard",
                    "Customer Churn Model",
                    "Resume Classifier AI",
                    "End-to-End ML Pipeline"
                ],
                "Cloud Engineer": [
                    "Deploy App on AWS",
                    "CI/CD Pipeline",
                    "Docker + Kubernetes Project",
                    "Monitoring Dashboard"
                ]
            }

            for proj in role_projects.get(role, []):
                st.write("•", proj)
