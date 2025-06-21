import streamlit as st
import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

st.title("LabWise")
st.write(
    "Upload your lab results below and ask a question about it."
    " To use this app, you need to provide an Anthropic API key, which you can get from your Anthropic account."
)

# Ask user for their Anthropic API key
anthropic_api_key = st.text_input("Anthropic API Key", type="password")
if not anthropic_api_key:
    st.info("Please add your Anthropic API key to continue.", icon="🗝️")
else:
    client = Anthropic(api_key=anthropic_api_key)

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

        # Generate completion (no streaming support currently in Anthropic SDK, so use sync call)
        response = client.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=1000,
            temperature=0.7,
        )

        st.write(response.completion)

