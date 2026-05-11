import streamlit as st 
import PyPDF2 
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Ai Resume Critiquer", page_icon="📄", layout="centered")

st.title("Ai Resume Critiquer")
st.markdown("Upload your resume and get Ai feedback!")

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf","txt"])
if uploaded_file and uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
    st.error("File size too large. Please upload a file smaller than 10MB.")
    st.stop()
job_role = st.text_input("Enter the job role/ position you are targeting")

analyze =st.button("Analyze Resume")

#Loading the text from the PDF or from TXT file
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

#If the button was pressed and there is a file, get all the context from that file. 
#If the file does not have any content, show an error message; if it does shows the prompt. 
if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)
        
        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()
            
        prompt = f"""
        You are an expert resume reviewer and career coach.

        Analyze the following resume and provide actionable, professional feedback tailored for {
            job_role if job_role else "general job applications"
        }.

        Your review should evaluate:

        1. Content Clarity & Professional Impact
        - Is the resume easy to scan and understand?
        - Are accomplishments clear, measurable, and relevant?
        - Is the overall narrative compelling?

        2. Skills Presentation
        - Are technical and soft skills organized effectively?
        - Are the most relevant skills prioritized?
        - Are there missing or outdated skills?

        3. Experience & Achievement Descriptions
        - Are bullet points achievement-oriented rather than task-oriented?
        - Are metrics, outcomes, and business impact included?
        - Are action verbs used effectively?
        - Are descriptions concise and ATS-friendly?

        4. Resume Structure & Formatting
        - Evaluate section organization, readability, and consistency.
        - Identify formatting or redundancy issues.
        - Assess ATS compatibility.

        5. Role-Specific Optimization
        - Suggest improvements specifically for {
            job_role if job_role else "general hiring relevance"
        }.
        - Recommend keywords, technologies, or experiences to emphasize.

        Resume Content:
        --------------------
        {file_content}
        --------------------

        Output Requirements:
        - Start with a brief overall assessment (2-4 sentences).
        - Then provide:
        • Strengths
        • Areas for Improvement
        • Specific Rewrite Suggestions
        • Missing Keywords or Skills
        • Final Recommendations
        - Use concise bullet points.
        - Prioritize high-impact improvements first.
        - Be honest, specific, and constructive.
        - Where possible, rewrite weak resume bullets into stronger versions.
        """
        
        # Create a OpenAI client and send the prompt to the API 
        client = OpenAI(api_key=OPEN_AI_KEY)
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                
                {"role": "user", "content": prompt}
                
            ],
            temperature = 0.7,
            max_tokens = 1000
        )
        st.markdown("### Analysis Results")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")