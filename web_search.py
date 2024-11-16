import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt', quiet=True)

def search_google(query, max_results=1):
    """
    Perform a Google search and return the first link.
    """
    from googlesearch import search

    try:
        results = []
        for url in search(query, num_results=max_results):
            results.append(url)
        return results[0] if results else None
    except Exception as e:
        print(f"Error during Google Search: {e}")
        return None


def fetch_and_summarize_content(url):
    """
    Fetch the content from the given URL and summarize it.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the main content (this may need to be adjusted per website)
        paragraphs = soup.find_all('p')
        content = " ".join([para.text for para in paragraphs])

        # Summarize the content
        summary = summarize_text(content)
        return summary
    except Exception as e:
        print(f"Error fetching or summarizing content: {e}")
        return "Failed to retrieve content."


def summarize_text(text, num_sentences=5):
    """
    Summarize the given text by extracting the first `num_sentences`.
    """
    sentences = sent_tokenize(text)
    return " ".join(sentences[:num_sentences])


def search_and_summarize(query):
    """
    Perform a search, fetch the first result, and summarize its content.
    """
    url = search_google(query)
    if url:
        summary = fetch_and_summarize_content(url)
        return {"url": url, "summary": summary}
    else:
        return {"url": None, "summary": "No results found."}
