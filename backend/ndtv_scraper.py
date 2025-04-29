import requests
from bs4 import BeautifulSoup

def scrape_ndtv():
    url = "https://www.ndtv.com/latest"
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
        print(f"Failed to retrieve NDTV News page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    news_articles = []
    seen_links = set()

    for article in soup.find_all("li", class_="NwsLstPg-a-li"):
        title_elem = article.find("a", class_="NwsLstPg_ttl-lnk")
        summary_elem = article.find("p", class_="NwsLstPg_txt")
        image_elem = article.find("img", class_="NwsLstPg_img-full")

        if not all([title_elem, summary_elem, image_elem]):
            continue

        title = title_elem.get_text(strip=True)
        summary = summary_elem.get_text(strip=True)
        link = title_elem.get("href", "").strip()
        image_url = image_elem.get("src", "").strip()

        if not link or link in seen_links:
            continue

        seen_links.add(link)
        news_articles.append({
            "Title": title,
            "Summary": summary,
            "Link": link,
            "Image": image_url,
            "website": "NDTV"
        })

    return news_articles
