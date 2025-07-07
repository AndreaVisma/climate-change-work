import requests
from bs4 import BeautifulSoup
import spacy

# Load Italian NLP model
nlp = spacy.load("it_core_news_sm")

# News website (example: ANSA)
URL = "https://www.ansa.it/sito/notizie/mondo/mondo.shtml"

def get_news_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find article links (adjust for different websites)
    articles = []
    for link in soup.find_all("a", href=True):
        if "/mondo/" in link["href"]:  # Adjust category if needed
            articles.append(link["href"])

    return list(set(articles))  # Remove duplicates

def extract_disaster_mentions(text):
    """Check if the text mentions a natural disaster"""
    disaster_keywords = ["terremoto", "alluvione", "uragano", "tsunami", "incendio", "inondazione", "siccità", "disastro"]
    doc = nlp(text.lower())

    mentions = [word for word in doc if word.text in disaster_keywords]
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]  # GPE = locations

    return mentions, locations


# Get articles
article_links = get_news_articles(URL)

# Process articles
for article_url in article_links:  # Limit to first 5 for testing
    full_url = f"https://www.ansa.it{article_url}"  # Adjust if needed
    article_page = requests.get(full_url)
    article_soup = BeautifulSoup(article_page.text, "html.parser")

    # Extract article text (adjust based on HTML structure)
    paragraphs = article_soup.find_all("p")
    article_text = " ".join([p.text for p in paragraphs])

    mentions, locations = extract_disaster_mentions(article_text)

    if mentions:
        print(f"🔴 Disaster Detected: {mentions} in {locations}")
        print(f"Article URL: {full_url}\n")
