import streamlit as st
import PyPDF2

st.set_page_config(page_title="AI Career Copilot", page_icon="🤖")

st.title("🤖 AI Career Copilot")
st.write("Upload your resume and get AI-based analysis")

# ----------- PDF TEXT EXTRACTOR -----------
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# ----------- ROLE SKILLS DATABASE -----------
roles = {
    "Software Developer": ["python", "java", "c++", "sql", "git", "api"],
    "Data Analyst": ["python", "excel", "sql", "power bi", "tableau", "statistics"],
    "Machine Learning Engineer": ["python", "tensorflow", "pytorch", "nlp", "deep learning"]
}

# ----------- FILE UPLOAD -----------
uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])

# ----------- ROLE SELECT -----------
selected_role = st.selectbox("Select Target Job Role", list(roles.keys()))

if uploaded_file is not None:
    resume_text = extract_text_from_pdf(uploaded_file)
    resume_lower = resume_text.lower()

    st.subheader("📄 Extracted Resume Text")
    st.text_area("", resume_text, height=200)

    # ----------- SKILL MATCHING -----------
    role_skills = roles[selected_role]
    matched_skills = []
    missing_skills = []

    for skill in role_skills:
        if skill in resume_lower:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    score = int((len(matched_skills) / len(role_skills)) * 100)

    # ----------- RESUME SCORE -----------
    st.subheader("📊 Resume Score")
    st.write(f"Score for {selected_role}: {score}/100")

    if score >= 80:
        st.success("Strong profile for this role!")
    elif score >= 50:
        st.warning("Good, but needs improvement.")
    else:
        st.error("Needs more relevant skills.")

    # ----------- MATCHED SKILLS -----------
    st.subheader("✅ Skills Found")
    st.write(matched_skills)

    # ----------- MISSING SKILLS -----------
    st.subheader("❌ Skills Missing")
    st.write(missing_skills)

    # ----------- ATS COMPATIBILITY CHECK (NEW FEATURE) -----------
    st.subheader("📊 ATS Compatibility Check")

    ats_score = 0

    if "skills" in resume_lower:
        ats_score += 20
    if "project" in resume_lower:
        ats_score += 20
    if "experience" in resume_lower:
        ats_score += 20
    if "education" in resume_lower:
        ats_score += 20
    if len(resume_text.split()) > 200:
        ats_score += 20

    st.write(f"ATS Score: {ats_score}/100")

    if ats_score >= 80:
        st.success("Your resume is ATS friendly!")
    elif ats_score >= 50:
        st.warning("Your resume is moderately ATS friendly. Add more keywords.")
    else:
        st.error("Your resume may not pass ATS. Improve structure & keywords.")
