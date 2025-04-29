import requests
from bs4 import BeautifulSoup
 

# Set headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# URL of Google News
url = "https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRE55YXpBU0JXVnVMVWRDS0FBUAE?hl=en-IN&gl=IN&ceid=IN:en"

# Retry settings
max_retries = 3
retry_delay = 2  # seconds

def scrape_google_news():
    news_items = []
    
    for attempt in range(max_retries):
        try:
            # Fetch the page with timeout
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise HTTP errors
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract articles
            for article in soup.select('article'):
                # Title
                title_elem = article.find('h3')
                title = title_elem.text if title_elem else "No title"
                
                # Link
                link_elem = article.find('a', href=True)
                if link_elem:
                    link = link_elem['href']
                    if link.startswith('./'):
                        link = "https://news.google.com" + link[1:]
                else:
                    link = "No link"
                
                # Source
                source_elem = article.find('div', {'aria-label': 'Source and timestamp'})
                source = source_elem.text.split('•')[0].strip() if source_elem else "Unknown"
                
                # Image
                img_elem = article.find('img')
                image_url = (
                    img_elem.get('src') or 
                    img_elem.get('data-src') or 
                    img_elem.get('data-lazy-src', 'No image')
                ) if img_elem else "No image"
                
                # Summary (Google News typically doesn't show summaries in initial HTML)
                summary_elem = article.find('p')
                summary = summary_elem.text if summary_elem else "Summary not available"
                
                news_items.append({
                    "Title": title,
                    "Summary": summary,
                    "Link": link,
                    "Image": image_url,
                    "Source": source
                })
            
            # If we got here, break out of retry loop
            break
            
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            
    
    return news_items

# Run scraper
news_data = scrape_google_news()
 