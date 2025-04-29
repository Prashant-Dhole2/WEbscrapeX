import requests
from bs4 import BeautifulSoup

def scrape_aajtak_india():
    url = "https://www.aajtak.in/india"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Aaj Tak India page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    news_articles = []
    seen_links = set()  # To track unique article links

    # Targeting Aaj Tak's article containers
    for article in soup.find_all("div", class_="story__card"):
        title_elem = article.find("h2", class_="title")
        summary_elem = article.find("p", class_=lambda c: c and "summary" in c.lower())
        link_elem = article.find("a", href=True)
        image_elem = article.find("img", class_=lambda c: not c or "lazyload" in c)

        # Skip if any critical field is missing
        if not all([title_elem, link_elem]):
            continue

        title = title_elem.text.strip()
        summary = summary_elem.text.strip() if summary_elem else ""
        link = "https://www.aajtak.in" + link_elem["href"] if link_elem["href"].startswith("/") else link_elem["href"]
        
        # Handle image URL (check both src and data-src)
        image_url = ""
        if image_elem:
            image_url = image_elem.get("src") or image_elem.get("data-src", "")
            if image_url and not image_url.startswith(("http", "www")):
                image_url = "https://www.aajtak.in" + (image_url if image_url.startswith("/") else "/" + image_url)

        # Skip if link is already processed
        if link in seen_links:
            continue

        seen_links.add(link)
        news_articles.append({
            "Title": title,
            "Summary": summary,
            "Link": link,
            "Image": image_url,
            "website": "Aaj Tak India"
        })

    return news_articles

# Example usage
if __name__ == "__main__":
    print("Scraping Aaj Tak India...")
    articles = scrape_aajtak_india()
    print(f"Found {len(articles)} articles")
    for i, article in enumerate(articles[:5], 1):  # Print first 5 articles
        print(f"\nArticle {i}:")
        print(f"Title: {article['Title']}")
        print(f"Summary: {article['Summary']}")
        print(f"Link: {article['Link']}")
        print(f"Image: {article['Image'][:50]}..." if article['Image'] else "No image")