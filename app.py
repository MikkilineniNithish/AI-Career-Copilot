import streamlit as st
import PyPDF2

st.set_page_config(page_title="AI Career Copilot", page_icon="🤖")

st.title("🤖 AI Career Copilot")
st.write("Upload your resume and get smart analysis")

role = st.selectbox(
    "Select target job role:",
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
        skills = ["Python", "Java", "C++", "SQL", "Git", "HTML", "CSS", "JavaScript"]
    elif role == "Data Scientist":
        skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]
    else:
        skills = ["AWS", "Cloud", "Linux", "Docker", "Python"]

    st.subheader("Resume Analysis")

    found_skills = []
    for skill in skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    st.write("### Skills Found:")
    st.write(found_skills)

    missing_skills = [skill for skill in skills if skill not in found_skills]

    st.write("### Skills Missing:")
    st.write(missing_skills)

    # Resume Score
    st.subheader("Resume Score")
    score = int((len(found_skills) / len(skills)) * 100)
    st.write(f"Score: {score}/100")

    # ⭐ NEW FEATURE — ATS CHECK
    st.subheader("ATS Compatibility Score")

    ats_score = 0
    if "skills" in text.lower():
        ats_score += 20
    if "project" in text.lower():
        ats_score += 20
    if "experience" in text.lower():
        ats_score += 20
    if "education" in text.lower():
        ats_score += 20
    if len(text.split()) > 200:
        ats_score += 20

    st.write(f"ATS Score: {ats_score}/100")

    if ats_score > 70:
        st.success("ATS Friendly Resume")
    elif ats_score > 40:
        st.warning("Improve resume formatting & keywords")
    else:
        st.error("Low ATS compatibility")
