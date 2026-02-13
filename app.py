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

    st.title("🎯 Welcome to AI Career Copilot")
    st.write("You are successfully logged in!")

    # -----------------------------
    # FEATURE 1: RESUME UPLOAD
    # -----------------------------
    st.header("📄 Upload Resume")

    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if uploaded_file:
        resume_text = uploaded_file.read().decode(errors="ignore")

        db.collection("resumes").document(st.session_state.user_email).set({
            "resume_text": resume_text
        })

        st.success("Resume saved successfully!")

    st.divider()

    # Upcoming features
    st.header("Next Features Coming:")
    st.write("• ATS Score")
    st.write("• JD Match")
    st.write("• Career Suggestions")
    st.write("• PDF Report")
