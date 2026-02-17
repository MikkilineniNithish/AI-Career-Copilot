import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="AI Career Copilot", layout="wide")

# ----------------------------
# SESSION STATE INITIALIZATION
# ----------------------------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "total_users" not in st.session_state:
    st.session_state.total_users = 0

if "total_reports" not in st.session_state:
    st.session_state.total_reports = 0

if "beginner_count" not in st.session_state:
    st.session_state.beginner_count = 0

if "intermediate_count" not in st.session_state:
    st.session_state.intermediate_count = 0

if "strong_count" not in st.session_state:
    st.session_state.strong_count = 0


# ----------------------------
# SIDEBAR MENU
# ----------------------------
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Generate Roadmap", "Admin Dashboard"]
)

# ----------------------------
# HOME PAGE
# ----------------------------
if menu == "Home":
    st.title("🚀 AI Career Copilot")
    st.write("Generate Personalized Roadmap + Suggested Projects")
    st.success("Build your career like a Strong Candidate 🔥")


# ----------------------------
# GENERATE ROADMAP
# ----------------------------
elif menu == "Generate Roadmap":

    st.title("📌 Personalized Learning Roadmap")

    name = st.text_input("Enter Your Name")
    domain = st.selectbox(
        "Select Your Domain",
        ["AI/ML", "Web Development", "Cloud", "Data Science"]
    )

    skill_level = st.selectbox(
        "Select Your Current Level",
        ["Beginner", "Intermediate", "Strong"]
    )

    if st.button("Generate Roadmap"):

        st.session_state.total_users += 1
        st.session_state.total_reports += 1

        # Track level count
        if skill_level == "Beginner":
            st.session_state.beginner_count += 1
            level_color = "🟢 Beginner"
        elif skill_level == "Intermediate":
            st.session_state.intermediate_count += 1
            level_color = "🟡 Intermediate"
        else:
            st.session_state.strong_count += 1
            level_color = "🔴 Strong Candidate"

        st.success(f"Roadmap Generated for {name}")
        st.markdown(f"### Level: {level_color}")

        # ---------------- ROADMAP + PROJECTS ----------------
        if domain == "AI/ML":
            roadmap = """
1. Python Basics
2. Numpy & Pandas
3. Machine Learning Algorithms
4. Deep Learning
5. Build Real-world AI Projects
"""
            projects = [
                "Face Recognition Attendance System",
                "AI Resume Analyzer",
                "Deepfake Detection App"
            ]

        elif domain == "Web Development":
            roadmap = """
1. HTML, CSS
2. JavaScript
3. React
4. Backend (Node/Django)
5. Deploy Full Stack App
"""
            projects = [
                "Portfolio Website",
                "E-commerce App",
                "Admin Dashboard System"
            ]

        elif domain == "Cloud":
            roadmap = """
1. Linux Basics
2. Networking
3. AWS Core Services
4. Docker
5. CI/CD Deployment
"""
            projects = [
                "AWS EC2 Deployment",
                "Cloud Monitoring Dashboard",
                "Cost Optimization Tracker"
            ]

        else:
            roadmap = """
1. Python
2. SQL
3. Pandas
4. Data Visualization
5. Build Analytics Dashboard
"""
            projects = [
                "Sales Analytics Dashboard",
                "Stock Market Analyzer",
                "Student Performance Tracker"
            ]

        st.subheader("📚 Learning Roadmap")
        st.text(roadmap)

        st.subheader("💡 Suggested Projects")
        for p in projects:
            st.write("✅", p)

        # ---------------- PDF GENERATION ----------------
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.multi_cell(
            0, 8,
            f"AI Career Copilot Report\n\n"
            f"Name: {name}\n"
            f"Level: {skill_level}\n"
            f"Domain: {domain}\n\n"
            f"Roadmap:\n{roadmap}"
        )

        pdf.output("roadmap.pdf")

        with open("roadmap.pdf", "rb") as f:
            st.download_button(
                "📄 Download PDF Report",
                f,
                file_name="roadmap.pdf"
            )


# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
elif menu == "Admin Dashboard":

    if not st.session_state.admin_logged_in:

        st.title("🔐 Admin Login")

        email = st.text_input("Admin Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if email == "copilotaicareer@gmail.com" and password == "admin123":
                st.session_state.admin_logged_in = True
                st.success("Login Successful ✅")
            else:
                st.error("Invalid Credentials ❌")

    else:
        st.title("📊 Admin Dashboard")

        col1, col2 = st.columns(2)
        col1.metric("Total Users", st.session_state.total_users)
        col2.metric("Total Reports", st.session_state.total_reports)

        st.markdown("---")

        st.subheader("👨‍💻 Candidate Level Distribution")

        st.write("🟢 Beginner:", st.session_state.beginner_count)
        st.write("🟡 Intermediate:", st.session_state.intermediate_count)
        st.write("🔴 Strong:", st.session_state.strong_count)

        st.markdown("---")
        st.success("🟢 Website Status: Running")

        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.success("Logged Out Successfully")
