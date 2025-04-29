import requests
from bs4 import BeautifulSoup

def scrape_timesofindia():
    url = "https://timesofindia.indiatimes.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Times of India page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    news_articles = []

    # Main featured articles
    for article in soup.find_all("div", class_="col_l_6")[:15]:  # Limit to 15 articles
        title = article.find("span", itemprop="    ")
        summary = article.find("figcaption", class_="    ")
        link = article.find("a", href=True)
        image = article.find("img", src=True)
        time_tag = article.find("span", class_="time_cptn")

        # Process fields
        article_data = {
            "Title": title.get_text(strip=True) if title else "N/A",
            "Summary": summary.get_text(strip=True) if summary else "N/A",
            "Link": "https://timesofindia.indiatimes.com" + link["href"] if link and link["href"].startswith("/") 
                   else link["href"] if link else "N/A",
            "Image": image["src"] if image else "N/A",
            "Time": time_tag.get_text(strip=True) if time_tag else "N/A",
            "Source": "Times of India"
        }

        # Only add articles that have at least a title and link
        if article_data["Title"] != "N/A" and article_data["Link"] != "N/A":
            news_articles.append(article_data)

    # Display results 

    return news_articles[:10]  # Return only first 10 articles

# Call the function
scrape_timesofindia()