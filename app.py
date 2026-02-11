import streamlit as st
import PyPDF2

st.set_page_config(page_title="AI Career Copilot", page_icon="🤖", layout="centered")

st.title("🤖 AI Career Copilot")
st.markdown("### Your Smart Resume Analyzer + ATS Checker")

role = st.selectbox(
    "🎯 Select your target job role:",
    ["Software Developer", "Data Scientist", "Cloud Engineer"]
)

uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])

def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)

    st.divider()
    st.subheader("📜 Extracted Resume Text")
    st.write(text[:1500])   # limit preview

    # Role-based skills
    if role == "Software Developer":
        skills = ["Python", "Java", "C++", "SQL", "Git", "HTML", "CSS", "JavaScript"]
    elif role == "Data Scientist":
        skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]
    else:
        skills = ["AWS", "Cloud", "Linux", "Docker", "Python"]

    st.divider()
    st.subheader("🧠 Resume Analysis")

    found_skills = []
    for skill in skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    st.write("### ✅ Skills Found")
    st.write(found_skills if found_skills else "No matching skills found")

    missing_skills = [skill for skill in skills if skill not in found_skills]

    st.write("### ❌ Skills Missing")
    st.write(missing_skills)

    # Resume Score
    st.divider()
    st.subheader("📊 Resume Strength Score")

    score = int((len(found_skills) / len(skills)) * 100)
    st.progress(score)
    st.write(f"### {score}/100")

    if score > 70:
        st.success("🔥 Strong resume for this role!")
    elif score > 40:
        st.warning("⚡ Good start! Add more relevant skills.")
    else:
        st.error("🚨 Resume needs improvement.")

    # ATS SCORE
    st.divider()
    st.subheader("🤖 ATS Compatibility Score")

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

    st.progress(ats_score)
    st.write(f"### {ats_score}/100")

    if ats_score > 70:
        st.success("✅ ATS Friendly Resume")
    elif ats_score > 40:
        st.warning("⚠️ Improve formatting & keywords")
    else:
        st.error("❌ Low ATS compatibility")

    # AI Suggestions
    st.divider()
    st.subheader("💡 Smart Improvement Tips")

    if missing_skills:
        for skill in missing_skills[:5]:
            st.write(f"• Try adding **{skill}** to improve your chances")

    if ats_score < 60:
        st.write("• Add clear sections: Skills, Projects, Experience, Education")
        st.write("• Use more keywords from job descriptions")
        st.write("• Keep resume length at least 1 page")

    st.divider()
    st.subheader("🚀 Recommended Projects For You")

    if "Python" in found_skills:
        st.write("• AI Chatbot using Python")
        st.write("• Resume Analyzer Web App")

    if "AWS" in found_skills or role == "Cloud Engineer":
        st.write("• AWS Cloud File Upload System")
        st.write("• Deploy website using EC2")

    if "Machine Learning" in found_skills or role == "Data Scientist":
        st.write("• House Price Prediction Model")
        st.write("• Student Performance Predictor")

    if not found_skills:
        st.write("• Start with a basic Python project")
        st.write("• Build a personal portfolio website")
