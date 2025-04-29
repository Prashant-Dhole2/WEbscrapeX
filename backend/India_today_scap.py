import requests
from bs4 import BeautifulSoup

def scrape_india_today():
    url = "https://www.indiatoday.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve India Today page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    news_articles = []
    seen_links = set()

    # Find all articles with the specific class pattern
    for article in soup.find_all("article", class_=lambda c: c and "B1S3_story__card" in c):
        # Skip ads/sponsored content
        if article.find(class_=lambda c: c and any(x in c.lower() for x in ["ad", "promo", "sponsored"])):
            continue

        # Extract category
        category_elem = article.find("h4", class_=lambda c: c and "B1S3_cat__title" in c)
        category = category_elem.text.strip() if category_elem else "General"

        # Extract title and link
        title_elem = article.find("h2").find("a") if article.find("h2") else None
        if not title_elem:
            continue
            
        title = title_elem.get("title", "").strip() or title_elem.text.strip()
        link = title_elem["href"]
        if not link.startswith(("http", "www")):
            link = "https://www.indiatoday.in" + (link if link.startswith("/") else "/" + link)

        # Skip duplicates
        if link in seen_links:
            continue
        seen_links.add(link)

        # Extract summary
        summary_elem = article.find("div", class_=lambda c: c and "B1S3_story__shortcont" in c)
        summary = summary_elem.text.strip() if summary_elem else ""

        # Extract image
        img_elem = article.find("img", class_="image_one_to_one")
        image_url = img_elem["src"] if img_elem else ""

        news_articles.append({
            "Category": category,
            "Title": title,
            "Summary": summary,
            "Link": link,
            "Image": image_url,
            "website": "India Today"
        })

    return news_articles

# Test the function
if __name__ == "__main__":
    print("Scraping India Today...")
    articles = scrape_india_today()
    print(f"Found {len(articles)} articles")
    for i, article in enumerate(articles[:5], 1):  # Print first 5 articles
        print(f"\nArticle {i}:")
        print(f"Category: {article['Category']}")
        print(f"Title: {article['Title']}")
        print(f"Summary: {article['Summary']}")
        print(f"Link: {article['Link']}")
        print(f"Image: {article['Image'][:50]}..." if article['Image'] else "No image")