import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt', quiet=True)


def custom_search(query):
    """
    Perform a custom search using publicly available websites like Wikipedia.
    """
    search_url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return None


def extract_and_summarize_content(html_content):
    """
    Extract and summarize the content from the fetched HTML.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = " ".join([para.text for para in paragraphs if para.text.strip()])
        summary = summarize_text(content)
        return summary
    except Exception as e:
        print(f"Error extracting content: {e}")
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
    html_content = custom_search(query)
    if html_content:
        summary = extract_and_summarize_content(html_content)
        return {"url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}", "summary": summary}
    else:
        return {"url": None, "summary": "No results found or content could not be retrieved."}
