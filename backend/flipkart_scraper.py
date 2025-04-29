import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_flipkart(product):
    url = f"https://www.flipkart.com/search?q={product}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if "html" not in response.text.lower():
            print("Received non-HTML response from Flipkart")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Flipkart page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    products = []

    for item in soup.find_all("div", class_="cPHDOP col-12-12"):
        try:
            # Get all elements first
            name = item.find("div", class_="KzDlHZ")
             
            price = item.find("div", class_="Nx9bqj")
            rating = item.find("div", class_="XQDdHH")
            reviews = item.find("span", class_="_2_R_DZ")
            image = item.find("img", class_="DByuf4")
            link_elem = item.find("a", href=True)

            # Skip this product if any critical field is missing
            if not all([name, price, rating,image]):
                continue

            # Process data
            name = name.text.strip()
            price = float(price.text.replace("₹", "").replace(",", ""))
            rating = float(rating.text)
            product_url = "https://www.flipkart.com" + link_elem["href"] if link_elem["href"].startswith("/") else link_elem["href"]

            image_url = image["src"] if image else ""

            # Process reviews
            reviews_count = 0
            if reviews:
                reviews_text = reviews.text.strip()
                if "Ratings" in reviews_text:
                    reviews_count = int(reviews_text.split()[0].replace(",", ""))

            products.append({
                "Name": name,
                "Price": price,
                 
                "Rating": rating,
                "Reviews": reviews_count,
                "Image": image_url,
               "Link" : product_url,
                "Website": "Flipkart"
            })
            
        except Exception as e:
            print(f"Error processing product: {e}")
            continue

    if not products:
        print("No complete products found. Possible issues:")
        print("1. Flipkart has changed its HTML structure")
        print("2. Your IP might be temporarily blocked")
        print("3. Try different headers or add cookies")
        
        with open("flipkart_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved response HTML to flipkart_debug.html")

    return products