import requests
from bs4 import BeautifulSoup
import re

def scrape_walmart(product):
    url = f"https://www.walmart.com/search?q={product.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Walmart page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    seen_products = set()

    # Updated selectors for Walmart's current layout
    product_containers = soup.find_all("div", {"data-item-id": True})
    
    if not product_containers:
        # Alternative selector if the primary one fails
        product_containers = soup.find_all("div", class_=re.compile(r"mb\d|ph\d|pa\d-xl|w_\d+"))

    for item in product_containers:
        # Skip ads or sponsored items
        if item.find("span", string=re.compile("Sponsored", re.I)):
            continue
            
        # NAME - using multiple possible selectors
        name_elem = (item.find("span", class_=re.compile(r"w_iUH7|f6|f7")) or  # Title classes
                    item.find("a", class_=re.compile(r"absolute|product-title")) or
                    item.find("span", {"itemprop": "name"}))
        
        # PRICE - looking for price-related elements
        price_elem = (item.find("div", class_=re.compile(r"price|currency|mr1")) or
                    item.find("span", class_=re.compile(r"w_iUH7|price-characteristic")) or
                    item.find("span", {"itemprop": "price"}))
        
        # IMAGE - flexible image selector
        image_elem = (item.find("img", class_=re.compile(r"absolute|product-image|w_DE")) or
                     item.find("img", {"data-pnodetype": "item-pimg"}))
        
        # LINK - product URL
        link_elem = (item.find("a", class_=re.compile(r"absolute|product-title-link")) or
                   item.find("a", href=re.compile(r"/ip/")))
        
        # RATING - review stars
        rating_elem = (item.find("span", class_=re.compile(r"stars|rating|w_DG|w_iUH7")) or
                      item.find("span", {"aria-label": re.compile(r"stars")}))
        
        # Skip if critical fields are missing
        if not all([name_elem, price_elem]):
            continue

        # Extract data with better error handling
        try:
            name = name_elem.get_text(strip=True)
            
            # Improved price parsing
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(",", ""))
            if not price_match:
                continue
                
            price = float(price_match.group())
            price1 = price * 85  # Currency conversion if needed
            
            # Get image URL
            image_url = ""
            if image_elem:
                image_url = image_elem.get("src") or image_elem.get("data-src", "")
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                elif image_url.startswith("/"):
                    image_url = "https://www.walmart.com" + image_url
            
            # Get product URL
            product_url = ""
            if link_elem:
                product_url = link_elem.get("href", "")
                if product_url.startswith("/"):
                    product_url = "https://www.walmart.com" + product_url.split("?")[0]
            
            # Create unique identifier
            product_id = f"{hash(name)}-{hash(str(price))}"
            
            if product_id in seen_products:
                continue
                
            seen_products.add(product_id)
            
            # Get rating if available
            rating = 0.0
            if rating_elem:
                rating_text = rating_elem.get("aria-label", "") or rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d\.?\d?) out of 5', rating_text)
                if not rating_match:
                    rating_match = re.search(r'\d\.?\d*', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Get reviews count if available
            reviews = 0
            reviews_elem = item.find("span", class_=re.compile(r"review|count|w_DH"))
            if reviews_elem:
                reviews_text = reviews_elem.get_text(strip=True)
                reviews_match = re.search(r'(\d+,?\d*)', reviews_text.replace(",", ""))
                if reviews_match:
                    reviews = int(reviews_match.group(1))

            products.append({
                "Name": name,
                "Price": price1,
                "Rating": rating,
                "Reviews": reviews,
                "Image": image_url,
                "Link": product_url,
                "Website": "Walmart"
            })
        except Exception as e:
            print(f"Error processing product: {e}")
            continue
        
    if not products:
        print("Walmart: No products found. Possible issues:")
        print("1. Walmart has changed its HTML structure")
        print("2. The request was blocked (try different headers/proxy)")
        print("3. No results for your search query")
        # Save the HTML for inspection
        with open("walmart_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved response HTML to walmart_debug.html")

    return products