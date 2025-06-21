import streamlit as st
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import PyPDF2
import docx

st.title("LabWise")

st.write("Upload your lab results below (txt, md, pdf, docx) and ask a question about it.")

ANTHROPIC_API_KEY = st.secrets.get("anthropic_api_key")  # Replace with your key or use env/secrets
client = Anthropic(api_key=ANTHROPIC_API_KEY)

uploaded_file = st.file_uploader(
    "Upload a document",
    type=["txt", "md", "pdf", "docx"]
)

def extract_text(file, file_type):
    if file_type in ["txt", "md"]:
        return file.read().decode()
    elif file_type == "pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif file_type == "docx":
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    else:
        return ""

question = st.text_area(
    "Now ask a question about the document!",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and question:
    file_type = uploaded_file.type.split("/")[-1]  # crude way to detect type, might vary
    # fallback: use extension if mimetype is inconsistent
    if not file_type or file_type not in ["plain", "pdf", "vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        if uploaded_file.name.endswith(".txt"):
            file_type = "txt"
        elif uploaded_file.name.endswith(".md"):
            file_type = "md"
        elif uploaded_file.name.endswith(".docx"):
            file_type = "docx"
        elif uploaded_file.name.endswith(".pdf"):
            file_type = "pdf"

    text = extract_text(uploaded_file, file_type)

    prompt = (
        HUMAN_PROMPT
        + f"Here's a document: {text} \n\n---\n\n {question}"
        + AI_PROMPT
    )

    response = client.completions.create(
        model="claude-2",
        prompt=prompt,
        max_tokens_to_sample=1000,
        temperature=0.7,
    )

    st.subheader("Explanation")
    st.write(response.completion)

