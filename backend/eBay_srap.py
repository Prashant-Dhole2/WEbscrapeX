import requests
from bs4 import BeautifulSoup

def scrape_ebay(product):
    url = f"https://www.ebay.com/sch/i.html?_nkw={product.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve eBay page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    seen_products = set()

    for item in soup.find_all("div", class_=["s-item__wrapper", "s-item-wrapper", "sresult", "lvresult"]):
        # Skip separator divs and ads
        if "s-item__sep" in item.get("class", []) or "s-item__advertisement" in item.get("class", []):
            continue
            
        # NAME with multiple fallback options
        name_elem = (item.find("h3", class_="s-item__title") or 
                    item.find("h2", class_="s-item__title") or
                    item.find("a", class_="s-item__link") or
                    item.find("h3", class_="lvtitle") or
                    item.find("a", class_="vip"))
        
        # PRICE with multiple fallback options
        price_elem = (item.find("span", class_="s-item__price") or
                     item.find("span", class_="prc") or
                     item.find("li", class_="lvprice") or
                     item.find("span", class_="bold") or
                     item.find("span", class_="price"))
        
        # IMAGE with multiple fallback options
        image_elem = (item.find("img", class_="s-item__image-img") or
                     item.find("img", class_="img") or
                     item.find("img", class_="lvpic") or
                     item.find("img", class_="s-item__image") or
                     item.find("img"))
        
        # LINK with multiple fallback options
        link_elem = (item.find("a", class_="s-item__link") or
                    item.find("a", class_="vip") or
                    item.find("a", class_="img") or
                    item.find("a", href=True))
        
        # REVIEWS with multiple fallback options
        reviews_elem = (item.find("span", class_="s-item__reviews-count") or
                       item.find("span", class_="review") or
                       item.find("span", class_="rating"))
        
        # Skip if critical fields are missing
        if not all([name_elem, price_elem, image_elem, link_elem]):
            continue

        # Extract data
        try:
            name = name_elem.text.strip()
            
            # Handle price (multiple formats)
            price_text = price_elem.text.strip()
            if "to" in price_text:  # Handle price ranges
                price = float(price_text.split()[0].replace("$", "").replace(",", ""))
            else:
                price = float(price_text.replace("$", "").replace(",", ""))
            price1 =price*85 
            
            image_url = image_elem.get("src") or image_elem.get("data-src", "")
            product_url = link_elem["href"].split("?")[0]  # Clean URL
            
            # Create unique identifier
            product_id = f"{name[:50]}-{price}-{image_url[-10:]}"
            
            if product_id in seen_products:
                continue
                
            seen_products.add(product_id)
            
            # Get rating if available
            rating = 0.0
            if reviews_elem:
                try:
                    rating_text = reviews_elem.text.strip()
                    rating = float(rating_text.split()[0].strip("()"))
                except (ValueError, AttributeError):
                    pass
            
            # Get reviews count if available
            reviews = 0
            if reviews_elem:
                try:
                    reviews_text = reviews_elem.text.strip()
                    if "sold" in reviews_text.lower():
                        # Handle "1,000+ sold" format
                        reviews = int(reviews_text.split()[0].replace(",", "").replace("+", ""))
                    else:
                        # Handle "(123)" ratings format
                        reviews = int(reviews_text.strip("()").replace(",", ""))
                except (ValueError, AttributeError):
                    pass

            products.append({
                "Name": name,
                "Price": price1,
                "Rating": reviews,
                "Reviews": rating,
                "Image": image_url,
                "Link": product_url,
                "Website": "eBay"
            })
        except (ValueError, AttributeError, KeyError) as e:
            print(f"Error processing product: {e}")
            continue

    return products