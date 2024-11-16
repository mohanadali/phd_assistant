import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt', quiet=True)

def custom_search(query):
    """
    Perform a custom search on Wikipedia by constructing the URL.
    """
    search_url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            return None  # Page not found
        else:
            raise Exception(f"Unexpected HTTP status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return None


def extract_and_summarize_content(html_content):
    """
    Extract and summarize the content from the fetched HTML.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract main content paragraphs
        paragraphs = soup.find_all('p')
        if not paragraphs:
            return "No content available to summarize."

        # Combine text from all paragraphs
        content = " ".join([para.get_text() for para in paragraphs if para.get_text().strip()])

        # Debugging: Print first few lines of content
        print("Extracted Content Sample:", content[:500])

        # Remove citations (e.g., [1], [2])
        content = remove_citations(content)

        # Summarize the content
        summary = summarize_text(content)
        return summary
    except Exception as e:
        print(f"Error extracting content: {e}")
        return "Failed to retrieve content."


def remove_citations(text):
    """
    Remove citation references like [1], [2] from the text.
    """
    import re
    return re.sub(r'\[\d+\]', '', text)


def summarize_text(text, num_sentences=5):
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
    html_content = custom_search(query)
    if html_content:
        summary = extract_and_summarize_content(html_content)
        url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        return {"url": url, "summary": summary}
    else:
        return {"url": None, "summary": "No results found or content could not be retrieved."}
