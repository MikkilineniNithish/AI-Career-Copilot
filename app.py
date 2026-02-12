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
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    users_ref = db.collection("users")
    users_ref.document(email).set({
        "email": email,
        "password": hash_password(password)
    })

def check_user(email, password):
    user_doc = db.collection("users").document(email).get()
    if user_doc.exists:
        stored_password = user_doc.to_dict()["password"]
        return stored_password == hash_password(password)
    return False

# -----------------------------
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------------
# LOGIN / SIGNUP UI
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
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

# -----------------------------
# MAIN APP AFTER LOGIN
# -----------------------------
else:
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🎯 Welcome to AI Career Copilot")

    st.write("You are successfully logged in!")

    st.header("Next Features Coming:")
    st.write("• Resume ATS Analysis")
    st.write("• JD Match Score")
    st.write("• Career Suggestions")
    st.write("• PDF Report Download")
