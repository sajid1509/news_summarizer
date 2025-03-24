import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
EXCLUDED_SITES = ["msn.com"]
def get_news_links(company_name):
    """Fetches non-JS news links from Bing Search."""
    search_url = f"https://www.bing.com/news/search?q={company_name}&form=QBNH"
    response = requests.get(search_url, headers=HEADERS)
    
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    
    for a_tag in soup.select("a.title"):
        href = a_tag["href"]
        if href.startswith("http") and "bing.com" not in href:
            if not any(blocked in href for blocked in EXCLUDED_SITES):
                links.append(href)
    
    return list(set(links))[:10]  # Get unique 10 links

def extract_article_content(url):
    """Extracts title, summary, and metadata from a news article."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()  # Enables automatic summarization
        
        return {
            "title": article.title,
            "summary": article.summary,
            "published_date": article.publish_date if article.publish_date else "Unknown",
            "url": url
        }
    except Exception as e:
        return None

def scrape_news(company_name):
    """Fetches and extracts news articles related to a company."""
    news_links = get_news_links(company_name)
    articles = []
    
    for link in news_links:
        article = extract_article_content(link)
        if article:
            articles.append(article)
        time.sleep(1)  # Avoids getting blocked
    
    return articles

