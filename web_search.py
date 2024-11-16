import requests
from bs4 import BeautifulSoup

def search_web(query, max_results=5):
    base_url = "https://arxiv.org/search/"
    params = {'query': query, 'searchtype': 'all'}
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    for result in soup.find_all('li', class_='arxiv-result')[:max_results]:
        title = result.find('p', class_='title').text.strip()
        summary = result.find('p', class_='abstract').text.strip()
        link = result.find('a', string="pdf")['href']
        results.append({'title': title, 'summary': summary, 'link': link})
    return results
