import streamlit as st
import PyPDF2

st.set_page_config(page_title="AI Career Copilot", page_icon="🚀")

st.title("🚀 AI Career Copilot")
st.write("Smart Resume Analyzer for AI & Cloud Career Roles")

role = st.selectbox(
    "Select your target role:",
    ["Data Scientist", "ML Engineer", "Cloud Engineer", "AI Engineer"]
)

uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

roles_skills = {
    "Data Scientist": ["python", "machine learning", "data science", "sql", "statistics", "pandas"],
    "ML Engineer": ["python", "tensorflow", "pytorch", "deep learning", "docker", "api"],
    "Cloud Engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "linux"],
    "AI Engineer": ["python", "machine learning", "deep learning", "nlp", "tensorflow", "pytorch"]
}

project_suggestions = {
    "aws": "Build a cloud file upload system using AWS S3",
    "docker": "Containerize an app using Docker",
    "kubernetes": "Deploy an app using Kubernetes",
    "machine learning": "Build a prediction model",
    "deep learning": "Build an image classifier",
    "nlp": "Create an AI chatbot",
    "sql": "Build a database project",
    "api": "Create a REST API using Flask"
}

if uploaded_file is not None:
    resume_text = extract_text_from_pdf(uploaded_file)
    resume_text_lower = resume_text.lower()

    target_skills = roles_skills[role]

    found_skills = []
    for skill in target_skills:
        if skill in resume_text_lower:
            found_skills.append(skill)

    missing_skills = [skill for skill in target_skills if skill not in found_skills]
    score = int((len(found_skills) / len(target_skills)) * 100)

    st.subheader(f"📊 Match Score for {role}")
    st.success(f"{score}% match")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Skills You Have")
        st.write(found_skills)

    with col2:
        st.subheader("❌ Skills Missing")
        st.write(missing_skills)

    st.subheader("🚀 Project Suggestions To Improve")
    for skill in missing_skills:
        if skill in project_suggestions:
            st.write(f"- {project_suggestions[skill]}")

    st.subheader("🧠 Resume Improvement Tips")

    if score < 40:
        st.warning("Your resume needs strong improvement for this role.")
        st.write("- Add more relevant skills")
        st.write("- Build 2–3 strong projects")
        st.write("- Mention internships or practical experience")

    elif score < 70:
        st.info("Good start, but you can improve.")
        st.write("- Add tools like Docker, APIs, or Cloud platforms")
        st.write("- Highlight your best projects clearly")
        st.write("- Add measurable achievements")

    else:
        st.success("Strong profile for this role!")
        st.write("- Focus on advanced projects")
        st.write("- Add certifications")
        st.write("- Start applying for internships/jobs")

st.write("---")
st.caption("Built by Nithish | Final Year B.Tech | AI & Cloud Career Project")
