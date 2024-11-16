import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt', quiet=True)

def fetch_wikipedia(query):
    """
    Fetch content from Wikipedia for the given query.
    """
    search_url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            return {"source": "Wikipedia", "html": response.text, "url": search_url}
        return None
    except Exception as e:
        print(f"Error fetching Wikipedia: {e}")
        return None


def fetch_dictionary(query):
    """
    Fetch content from Dictionary.com or similar websites.
    """
    search_url = f"https://www.dictionary.com/browse/{query.replace(' ', '-')}"
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            return {"source": "Dictionary.com", "html": response.text, "url": search_url}
        return None
    except Exception as e:
        print(f"Error fetching Dictionary.com: {e}")
        return None


def extract_content(source, html_content):
    """
    Extract meaningful content from the HTML based on the source.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        if source == "Wikipedia":
            paragraphs = soup.find_all('p')
            content = " ".join([para.get_text() for para in paragraphs if para.get_text().strip()])
            return remove_citations(content)

        if source == "Dictionary.com":
            definition = soup.find('span', class_="one-click-content")
            if definition:
                return definition.get_text()
            return "No definition found."

        return "No content available."
    except Exception as e:
        print(f"Error extracting content from {source}: {e}")
        return "Failed to retrieve content."


def remove_citations(text):
    """
    Remove citation references like [1], [2] from the text.
    """
    import re
    return re.sub(r'\[\d+\]', '', text)


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
    Perform a search, fetch the content, and summarize it.
    """
    # Try Wikipedia first
    result = fetch_wikipedia(query)
    if result:
        content = extract_content("Wikipedia", result["html"])
        summary = summarize_text(content)
        return {"url": result["url"], "summary": summary}

    # Fallback to Dictionary.com
    result = fetch_dictionary(query)
    if result:
        content = extract_content("Dictionary.com", result["html"])
        return {"url": result["url"], "summary": content}

    return {"url": None, "summary": "No results found or content could not be retrieved."}
