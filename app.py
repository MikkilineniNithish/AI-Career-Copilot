import streamlit as st
import PyPDF2

st.title("AI Resume Analyzer")

role = st.selectbox(
    "Select the job role you are targeting:",
    ["Software Developer", "Data Scientist", "Cloud Engineer"]
)

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Resume Text")
    st.write(text)

    # Role-based skills
    if role == "Software Developer":
        skills = ["Python", "Java", "C++", "SQL", "Git", "Data Structures", "HTML", "CSS", "JavaScript"]
    elif role == "Data Scientist":
        skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL", "Data Visualization"]
    else:
        skills = ["AWS", "Cloud", "Linux", "Docker", "Python", "Networking"]

    st.subheader("Resume Analysis")

    found_skills = []
    for skill in skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    st.write("### Skills Found in Resume:")
    if found_skills:
        st.write(found_skills)
    else:
        st.write("No matching skills found.")

    missing_skills = [skill for skill in skills if skill not in found_skills]

    st.write("### Suggested Skills to Add:")
    st.write(missing_skills[:5])

    # Resume Score
    st.subheader("Resume Score")
    score = int((len(found_skills) / len(skills)) * 100)
    st.write(f"Your Resume Score: {score}/100")

    if score > 70:
        st.success("Great resume! You have many relevant skills.")
    elif score > 40:
        st.warning("Good start, but you can improve by adding more skills.")
    else:
        st.error("You need to add more skills to strengthen your resume.")

    # Project Suggestions Feature
    st.subheader("Recommended Projects For You")

    if "Python" in found_skills:
        st.write("- Build a Chatbot using Python")
        st.write("- Create a Resume Analyzer (like this project)")
    
    if "AWS" in found_skills or role == "Cloud Engineer":
        st.write("- Build a Cloud File Upload System using AWS S3")
        st.write("- Deploy a website using AWS EC2")

    if "Machine Learning" in found_skills or role == "Data Scientist":
        st.write("- House Price Prediction Model")
        st.write("- Student Performance Prediction System")

    if not found_skills:
        st.write("- Start with a basic Python project")
        st.write("- Build a Personal Portfolio Website")
