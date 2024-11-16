app.py
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

document_processing.py
import PyPDF2
from docx import Document
import nltk
from nltk.tokenize import sent_tokenize
from nltk.probability import FreqDist

nltk.download('punkt')

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format."

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        text = f"Error extracting text from PDF: {e}"
    return text

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error extracting text from DOCX: {e}"

def summarize_text(text, num_sentences=5):
    try:
        sentences = sent_tokenize(text)
        return " ".join(sentences[:num_sentences])
    except Exception as e:
        return f"Error summarizing text: {e}"

def extract_keywords(text, num_keywords=5):
    try:
        words = [word.lower() for word in nltk.word_tokenize(text) if word.isalnum()]
        freq_dist = FreqDist(words)
        return [word for word, _ in freq_dist.most_common(num_keywords)]
    except Exception as e:
        return f"Error extracting keywords: {e}"

web_search.py
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import nltk

# Ensure the NLTK Punkt tokenizer is downloaded
nltk.download('punkt', quiet=True)

def search_google_snippet(query):
    """
    Perform a basic Google search and extract snippets from the results.
    """
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            snippets = soup.find_all("span", class_="aCOpRe")
            if snippets:
                return snippets[0].get_text()  # Return the first snippet
        return "No relevant information found."
    except Exception as e:
        return f"Error fetching Google results: {e}"

def search_dictionary(query):
    """
    Fetch a definition from Dictionary.com or a similar dictionary site.
    """
    search_url = f"https://www.dictionary.com/browse/{query.replace(' ', '-')}"
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            definition = soup.find("span", class_="one-click-content")
            if definition:
                return definition.get_text()
        return "No definition found."
    except Exception as e:
        return f"Error fetching dictionary results: {e}"

def summarize_text(text, num_sentences=3):
    """
    Summarize the given text by extracting the first `num_sentences`.
    """
    sentences = sent_tokenize(text)
    if not sentences:
        return "No content available to summarize."
    return " ".join(sentences[:num_sentences])

def search_and_summarize(query):
    """
    Perform a search, retrieve content from multiple sources, and summarize it.
    """
    # Attempt Google snippet first
    snippet = search_google_snippet(query)
    if snippet and snippet != "No relevant information found.":
        summary = summarize_text(snippet)
        return {"source": "Google Search", "summary": summary, "url": f"https://www.google.com/search?q={query.replace(' ', '+')}"}

    # Fallback to Dictionary.com for definitions
    definition = search_dictionary(query)
    if definition and definition != "No definition found.":
        return {"source": "Dictionary.com", "summary": definition, "url": f"https://www.dictionary.com/browse/{query.replace(' ', '-')}"}    

    # No results found
    return {"source": "None", "summary": "No results found or content could not be retrieved.", "url": None}
