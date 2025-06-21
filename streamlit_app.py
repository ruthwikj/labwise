import streamlit as st
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

st.title("LabWise")

st.write("Upload your lab results below and ask a question about it.")

# *** WARNING: Hardcoding API keys is insecure! ***
# Use this only for quick tests and remove the key immediately after.
ANTHROPIC_API_KEY = "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"

client = Anthropic(api_key=ANTHROPIC_API_KEY)

uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))

question = st.text_area(
    "Now ask a question about the document!",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and question:
    document = uploaded_file.read().decode()

    prompt = (
        HUMAN_PROMPT
        + f"Here's a document: {document} \n\n---\n\n {question}"
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
