import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import PyPDF2
import datetime
from fpdf import FPDF

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

        # ---------------- DISPLAY SCORES ----------------
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

        # ---------------- ROADMAP ----------------
        st.subheader("🧭 Personalized Learning Roadmap")

        if role == "Software Developer":
            roadmap = [
                "Learn Python/Java deeply",
                "Master DSA",
                "Build 5 projects",
                "Learn Git & System Design",
                "Apply for SDE roles"
            ]
        elif role == "Data Scientist":
            roadmap = [
                "Master Python & Pandas",
                "Learn Statistics",
                "Practice ML models",
                "Build data projects",
                "Apply for data roles"
            ]
        else:
            roadmap = [
                "Learn Linux basics",
                "Learn AWS core services",
                "Practice Docker",
                "Build cloud projects",
                "Get AWS certification"
            ]

        for step in roadmap:
            st.write("•", step)

        # ---------------- PROJECT SUGGESTIONS ----------------
        st.subheader("🚀 Suggested Projects")

        project_map = {
            "Python": ["AI Chatbot", "Automation Tool"],
            "AWS": ["Deploy website on EC2", "Serverless app"],
            "SQL": ["Library DB system"],
            "Machine Learning": ["Spam classifier"],
            "Docker": ["Containerize Flask app"],
            "Linux": ["Log monitoring tool"]
        }

        suggested_projects = []
        for skill in missing_skills:
            if skill in project_map:
                suggested_projects.extend(project_map[skill])

        if suggested_projects:
            for p in suggested_projects:
                st.write("•", p)
        else:
            st.write("🔥 Strong profile already!")

        # ---------------- PDF DOWNLOAD ----------------
        st.subheader("📄 Download PDF Report")

        if st.button("Generate Report"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="AI Career Copilot Report", ln=True)
            pdf.cell(200, 10, txt=f"Skill Score: {score}", ln=True)
            pdf.cell(200, 10, txt=f"ATS Score: {ats_score}", ln=True)

            pdf.output("report.pdf")

            with open("report.pdf", "rb") as f:
                st.download_button("Download Report", f, file_name="career_report.pdf")
