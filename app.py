import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import PyPDF2
import datetime
from fpdf import FPDF

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

# ---------------- PDF REPORT ----------------
def create_pdf(role, score, ats_score, jd_score, found_skills, missing_skills, level):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AI Career Copilot Report", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Role: {role}", ln=True)
    pdf.cell(200, 10, txt=f"Skill Score: {score}%", ln=True)
    pdf.cell(200, 10, txt=f"ATS Score: {ats_score}%", ln=True)
    pdf.cell(200, 10, txt=f"JD Match Score: {jd_score}%", ln=True)
    pdf.cell(200, 10, txt=f"Level: {level}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Skills Found:", ln=True)
    for s in found_skills:
        pdf.cell(200, 10, txt=f"- {s}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Missing Skills:", ln=True)
    for s in missing_skills:
        pdf.cell(200, 10, txt=f"- {s}", ln=True)

    return pdf.output(dest="S").encode("latin-1")

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

        # ---------------- LEVEL ----------------
        avg = int((score + ats_score + match_score)/3) if jd_text else int((score + ats_score)/2)

        if avg < 50:
            level = "Beginner"
            st.error("🔴 Beginner Profile")
        elif avg < 75:
            level = "Intermediate"
            st.warning("🟡 Intermediate Profile")
        else:
            level = "Strong Candidate"
            st.success("🟢 Strong Profile")

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

        # ---------------- SCORES ----------------
        st.subheader("📊 Skill Score")
        st.progress(score)
        st.write(score)

        st.subheader("🤖 ATS Score")
        st.progress(ats_score)
        st.write(ats_score)

        if jd_text:
            st.subheader("🎯 JD Match Score")
            st.progress(match_score)
            st.write(match_score)

        st.metric("Overall Performance", f"{avg}%")

        st.subheader("✅ Skills Found")
        st.write(found_skills)

        st.subheader("❌ Missing Skills")
        st.write(missing_skills)

        # ---------------- ROADMAP ----------------
        st.subheader("🧭 Personalized Learning Roadmap")

        if role == "Software Developer":
            roadmap = [
                "Learn Python/Java deeply",
                "Master DSA",
                "Build 5 projects",
                "Learn System Design",
                "Apply for SDE roles"
            ]
        elif role == "Data Scientist":
            roadmap = [
                "Python + Pandas",
                "Statistics",
                "Machine Learning",
                "Data projects",
                "Apply for DS roles"
            ]
        else:
            roadmap = [
                "Linux",
                "AWS Core Services",
                "Docker",
                "Deploy projects",
                "AWS Certification"
            ]

        for step in roadmap:
            st.write("•", step)

        # ---------------- PROJECTS ----------------
        st.subheader("🚀 Suggested Projects")

        project_map = {
            "Python": ["AI Chatbot", "Automation Script"],
            "SQL": ["Library DB System"],
            "Java": ["Banking App"],
            "AWS": ["Deploy website EC2+S3"],
            "Docker": ["Dockerize Flask app"],
            "Machine Learning": ["House Price Prediction"],
            "Linux": ["Shell automation"]
        }

        suggested = []
        for skill in missing_skills:
            if skill in project_map:
                suggested.extend(project_map[skill])

        if suggested:
            for p in suggested[:6]:
                st.write("•", p)
        else:
            st.write("Your profile is strong. Start applying!")

        # ---------------- PDF DOWNLOAD ----------------
        pdf_data = create_pdf(role, score, ats_score, match_score, found_skills, missing_skills, level)

        st.download_button(
            "📄 Download PDF Report",
            pdf_data,
            "career_report.pdf",
            "application/pdf"
        )
