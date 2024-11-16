import streamlit as st
from web_search import search_and_summarize
from document_processing import extract_text, summarize_text
import nltk

# Ensure the NLTK Punkt tokenizer is available
nltk.download('punkt', quiet=True)

# App Title
st.title("PhD Assistant AI")

# Section 1: Document Upload and Analysis
st.header("1. Document Upload and Analysis")
uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "docx"])
if uploaded_file:
    try:
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
    except Exception as e:
        st.error(f"Error processing the uploaded file: {e}")

# Section 2: Autonomous Web Search
st.header("2. Autonomous Web Search")
query = st.text_input("Enter your search query:")
if query:
    try:
        st.write("Searching the web...")
        result = search_and_summarize(query)
        if result["source"] != "None":
            st.subheader(f"Search Result from {result['source']}:")
            st.write(result["summary"])
            if result["url"]:
                st.markdown(f"[Read Full Article]({result['url']})")
        else:
            st.warning("No results found. Try another query.")
    except Exception as e:
        st.error(f"Error performing the search: {e}")

# Footer
st.write("Powered by PhD. students 2024-2025")
