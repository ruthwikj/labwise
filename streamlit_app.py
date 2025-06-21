import streamlit as st
from anthropic import Anthropic
import PyPDF2
import docx
import os

# ---- Custom CSS for colors and style ----
st.markdown(
    """
    <style>
    /* Page background */
    .reportview-container {
        background: #f0f4f8;
    }
    /* Header style */
    .css-1v3fvcr h1 {
        color: #1a73e8;  /* Google Blue */
        font-weight: 700;
    }
    /* Subtitle */
    .css-1v3fvcr p {
        color: #555555;
        font-size: 18px;
    }
    /* Text area */
    textarea {
        border: 2px solid #1a73e8 !important;
        border-radius: 8px !important;
        font-size: 16px;
        padding: 8px !important;
    }
    /* Button style */
    div.stButton > button {
        background-color: #1a73e8;
        color: white;
        font-weight: 600;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #155ab6;
        cursor: pointer;
    }
    /* Answer text */
    .stMarkdown p {
        font-size: 18px;
        color: #333333;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("LabWise")
st.write("Upload your lab results (txt, md, pdf, docx) and ask a question about them.")

ANTHROPIC_API_KEY = st.secrets.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    st.error("Anthropic API key not found.")
    st.stop()

client = Anthropic(api_key=ANTHROPIC_API_KEY)

uploaded_file = st.file_uploader("Upload a document", type=["txt", "md", "pdf", "docx"])

def extract_text(file, file_type):
    if file_type in ["txt", "md"]:
        return file.read().decode()
    elif file_type == "pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
    elif file_type == "docx":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

question = st.text_area(
    "Now ask a question about the document!",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

submit = st.button("Submit")

if submit and uploaded_file and question:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    text = extract_text(uploaded_file, file_ext)

    with st.spinner("Analyzing with Claude 3 Haiku..."):
        response = client.messages.create(
            model="claude-3-haiku",
            max_tokens=1000,
            temperature=0.5,
            messages=[
                {"role": "user", "content": f"Here's a document:\n{text}\n\nQuestion: {question}"}
            ]
        )

    st.subheader("Answer")
    st.write(response.content[0].text)
