import requests
from bs4 import BeautifulSoup

def scrape_bbc():
    url = "https://www.bbc.com/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = "utf-8"
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve BBC News page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    news_articles = []
    seen_links = set()

   # Existing format
    

    # New format: <div data-testid="dundee-card">
    for article in soup.find_all("div", attrs={"data-testid": "dundee-card"}):
        link_tag = article.find("a", attrs={"data-testid": "internal-link"})
        if not link_tag or not link_tag.has_attr("href"):
            continue

        link = "https://www.bbc.com" + link_tag["href"]
        if link in seen_links:
            continue

        title_elem = article.find("h2", attrs={"data-testid": "card-headline"})
        summary_elem = article.find("p", attrs={"data-testid": "card-description"})
        image_elem = article.find("img", class_="sc-4abb68ca-0 ldLcJe")

        if not all([title_elem, summary_elem, image_elem]):
            continue

        title = title_elem.text.strip()
        summary = summary_elem.text.strip()
        image_url = image_elem.get("src") or image_elem.get("data-src")

        seen_links.add(link)
        news_articles.append({
            "Title": title,
            "Summary": summary,
            "Link": link,
            "Image": image_url,
            "website": "BBC News"
        })

    return news_articles
