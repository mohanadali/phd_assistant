import streamlit as st
import nltk
from document_processing import extract_text, summarize_text
from web_search import search_web

st.title("PhD Assistant AI")

# Document Upload Section
st.header("1. Document Upload and Analysis")
uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "docx"])
if uploaded_file:
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    extracted_text = extract_text(file_path)
    st.subheader("Extracted Text:")
    st.write(extracted_text[:1000])  # Show a snippet
    summary = summarize_text(extracted_text)
    st.subheader("Summary:")
    st.write(summary)

# Web Search Section
st.header("2. Autonomous Web Search")
query = st.text_input("Enter your search query:")
if query:
    results = search_web(query)
    st.subheader("Search Results:")
    for idx, result in enumerate(results):
        st.write(f"### {idx + 1}. {result['title']}")
        st.write(result['summary'])
        st.markdown(f"[Read PDF]({result['link']})")

# Footer
st.write("Powered by Open-Source Tools.")
