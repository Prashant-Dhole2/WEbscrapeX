import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_alibaba(product): 
    url = f"https://www.alibaba.com/trade/search?SearchText={product.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Alibaba page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    seen_products = set()

    # Multiple container class options
    for item in soup.find_all("div", class_=["organic-gallery-offer-outter", 
                                           "organic-gallery__item",
                                           "list-no-v2-outter",
                                           "J-offer-wrapper",
                                           "item-main"]):
        # Skip ads and irrelevant items
        if "advertisement" in item.get("class", []):
            continue
            
        # NAME with multiple fallback options
        name_elem = (item.find("p", class_="elements-title-normal__content") or
                    item.find("h2", class_="title") or
                    item.find("a", class_="product-title") or
                    item.find("div", class_="product-name"))
        
        # PRICE with multiple fallback options
        price_elem = (item.find("span", class_="elements-offer-price-normal__price") or
                     item.find("span", class_="price") or
                     item.find("div", class_="price") or
                     item.find("span", class_="price-value"))
        
        # IMAGE with multiple fallback options
        image_elem = (item.find("img", class_="seb-img-switcher__img") or
                     item.find("img", class_="product-image") or
                     item.find("img", loading="lazy") or
                     item.find("img", class_="main-img"))
        
        # LINK with multiple fallback options
        link_elem = (item.find("a", class_="elements-title-normal") or
                    item.find("a", class_="product-link") or
                    item.find("a", href=True))
        
        # RATING with multiple fallback options
        rating_elem = (item.find("span", class_="seb-supplier-review__score") or
                      item.find("span", class_="rating-stars") or
                      item.find("div", class_="star-rate"))
        
        # REVIEWS with multiple fallback options
        reviews_elem = (item.find("span", class_="seb-supplier-review__review-count") or
                       item.find("span", class_="review-count") or
                       item.find("div", class_="total-reviews"))
        
        # Skip if critical fields are missing
        if not all([name_elem, price_elem, image_elem, link_elem]):
            continue

        # Extract data
        try:
            name = name_elem.text.strip()
            
            # Handle price (multiple formats)
            price_text = price_elem.text.strip()
            if "-" in price_text:  # Handle price ranges
                price = float(price_text.split("-")[0].replace("$", "").replace(",", "").strip())
            else:
                price = float(price_text.replace("$", "").replace(",", ""))
            price_inr = price * 85  # Convert USD to INR
            
            image_url = image_elem.get("src") or image_elem.get("data-src", "")
            if image_url.startswith("//"):
                image_url = "https:" + image_url
                
            product_url ="https://www.alibaba.com" + link_elem["href"] if link_elem["href"].startswith("/") else link_elem["href"]
            
            product_url = product_url.split("?")[0]  # Clean URL
            
            # Create unique identifier
            product_id = f"{name[:50]}-{price}-{image_url[-10:]}"
            
            if product_id in seen_products:
                continue
                
            seen_products.add(product_id)
            
            # Get rating if available
            rating = 0.0
            if rating_elem:
                try:
                    rating_text = rating_elem.text.strip()
                    if "%" in rating_text:  # Handle percentage ratings
                        rating = float(rating_text.replace("%", "")) / 20  # Convert to 5-star scale
                    else:
                        rating = float(rating_text.split()[0])
                except (ValueError, AttributeError):
                    pass
            
            # Get reviews count if available
            reviews = 0
            if reviews_elem:
                try:
                    reviews_text = reviews_elem.text.strip()
                    reviews = int(reviews_text.replace(",", "").replace("(", "").replace(")", ""))
                except (ValueError, AttributeError):
                    pass

            products.append({
                "Name": name,
                "Price": price_inr,  # Price in INR like eBay version
                "Rating": rating,    # Rating out of 5
                "Reviews": reviews,  # Number of reviews
                "Image": image_url,
                "Link": product_url,
                "Website": "Alibaba"
            })
        except (ValueError, AttributeError, KeyError) as e:
            print(f"Error processing product: {e}")
            continue
    if not products:
        print(" alibaba No products found. Possible issues:")
    return products