import streamlit as st
from anthropic import Anthropic
import PyPDF2
import docx
import os

# --- Custom CSS ---
st.markdown(
    """
    <style>
    /* Background */
    .reportview-container {
        background: #f0f4f8;
    }
    /* Header */
    .css-1v3fvcr h1 {
        color: #1a73e8;
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
    /* Green submit button */
    div.stButton > button {
        background-color: #28a745;
        color: white;
        font-weight: 600;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #1e7e34;
        cursor: pointer;
    }
    /* Answer */
    .stMarkdown p {
        font-size: 18px;
        color: #333333;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
st.sidebar.title("LabWise Settings")
max_tokens = st.sidebar.slider("Max tokens", 100, 2000, 1000, step=100)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5, step=0.05)

# --- Main app ---
st.title("LabWise")
st.write("Upload your lab results (txt, md, pdf, docx) and ask a question about them.")

ANTHROPIC_API_KEY = st.secrets.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    st.error("Anthropic API key not found. Please set it in Streamlit secrets or environment variables.")
    st.stop()

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Layout with two columns
col1, col2 = st.columns([2, 3])

with col1:
    uploaded_file = st.file_uploader("Upload a document", type=["txt", "md", "pdf", "docx"])

with col2:
    question = st.text_area(
        "Ask a question about the document:",
        placeholder="E.g., Can you summarize the key points?",
        disabled=not uploaded_file,
        height=150
    )
    submit = st.button("Submit")

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

if submit:
    if not uploaded_file:
        st.warning("Please upload a document first.")
    elif not question.strip():
        st.warning("Please enter a question about the document.")
    else:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        text = extract_text(uploaded_file, file_ext)

        with st.spinner("Analyzing with Claude 3 Haiku..."):
            response = client.messages.create(
                model="claude-3-haiku",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": f"Here's a document:\n{text}\n\nQuestion: {question}"}
                ]
            )

        st.subheader("Answer")
        st.write(response.content[0].text)
