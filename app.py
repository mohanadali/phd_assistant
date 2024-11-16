import streamlit as st
import nltk
from document_processing import extract_text, summarize_text
from web_search import search_and_summarize

# Ensure NLTK data is downloaded
nltk.download('punkt', quiet=True)

# App Title
st.title("PhD Assistant AI")

# Section 1: Document Upload and Analysis
st.header("1. Document Upload and Analysis")
uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "docx"])
if uploaded_file:
    # Save the uploaded file temporarily
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Extract text from the document
    extracted_text = extract_text(file_path)
    st.subheader("Extracted Text:")
    st.write(extracted_text[:1000])  # Show a snippet of the extracted text
    # Summarize the extracted text
    summary = summarize_text(extracted_text)
    st.subheader("Summary:")
    st.write(summary)

# Section 2: Autonomous Web Search and Summarization
st.header("2. Autonomous Web Search")
query = st.text_input("Enter your search query:")
if query:
    st.write("Searching Wikipedia...")
    # Perform search and summarization
    result = search_and_summarize(query)
    if result["url"]:
        st.subheader("Search Result Summary:")
        st.write(result["summary"])
        st.markdown(f"[Read Full Article]({result['url']})")
    else:
        st.warning("No results found. Try another query.")

# Footer
st.write("Powered by PhD. students 2024-2025")
