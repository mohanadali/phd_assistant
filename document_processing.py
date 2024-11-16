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
