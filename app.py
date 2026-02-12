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

jd_text = st.text_area("📋 Paste Job Description Here (Optional for Match Score)")

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
    st.subheader("📜 Extracted Resume Preview")
    st.write(text[:1500])

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

    missing_skills = [skill for skill in skills if skill not in found_skills]

    st.write("### ✅ Skills Found")
    st.write(found_skills if found_skills else "No matching skills found")

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

    # ATS Score
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

    # AI Feedback
    st.divider()
    st.subheader("🧠 AI Career Coach Feedback")

    feedback = []

    if "experience" not in text.lower():
        feedback.append("Add an EXPERIENCE section to increase selection chances.")

    if "project" not in text.lower():
        feedback.append("Include PROJECTS. Recruiters love practical work.")

    if len(found_skills) < 3:
        feedback.append("Add more technical SKILLS relevant to your role.")

    if len(text.split()) < 250:
        feedback.append("Your resume looks short. Try adding more content.")

    if "achieve" not in text.lower() and "award" not in text.lower():
        feedback.append("Mention achievements or certifications to stand out.")

    if feedback:
        for tip in feedback:
            st.write("•", tip)
    else:
        st.success("Your resume looks strong and well structured!")

    # JD Match Score
    st.divider()
    st.subheader("📊 Resume vs Job Description Match Score")

    if jd_text:
        jd_words = jd_text.lower().split()
        resume_words = text.lower().split()

        common_words = set(jd_words).intersection(set(resume_words))

        if len(set(jd_words)) > 0:
            match_score = int((len(common_words) / len(set(jd_words))) * 100)
        else:
            match_score = 0

        st.progress(match_score)
        st.write(f"### Match Score: {match_score}%")

        if match_score > 70:
            st.success("🔥 Strong match! High chance for shortlist.")
        elif match_score > 40:
            st.warning("⚡ Moderate match. Improve resume with more JD keywords.")
        else:
            st.error("🚨 Low match. Add more skills/keywords from job description.")
