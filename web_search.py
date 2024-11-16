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
            snippets = soup.select("div.BNeawe.s3v9rd.AP7Wnd")  # Updated selector for Google snippets
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
