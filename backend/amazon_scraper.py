import requests
from bs4 import BeautifulSoup

def scrape_amazon(product):
    url = f"https://www.amazon.in/s?k={product.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Amazon page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    seen_products = set()  # To track unique products

    for item in soup.find_all("div", class_="s-result-item"):
        # Find all required elements
        name_elem = item.find("span", class_="a-size-medium") or \
                   item.find("a", class_="a-link-normal s-line-clamp-2 s-link-style a-text-normal")
        price_elem = item.find("span", class_="a-price-whole")
        rating_elem = item.find("span", class_="a-icon-alt")
        image_elem = item.find("img", class_="s-image")
        link_elem = item.find("a", class_="a-link-normal")

        # Skip if any critical field is missing
        if not all([name_elem, price_elem, rating_elem, image_elem, link_elem]):
            continue

        # Extract data
        try:
            name = name_elem.text.strip()
            price = float(price_elem.text.replace(",", ""))
            rating = float(rating_elem.text.split()[0])
            image_url = image_elem["src"]
            product_url = "https://www.amazon.in" + link_elem["href"] if link_elem["href"].startswith("/") else link_elem["href"]
            
            # Create unique identifier to detect duplicates
            product_id = f"{name[:50]}-{price}"
            
            if product_id in seen_products:
                continue
                
            seen_products.add(product_id)
            
            # Get reviews count if available
            reviews = 0
            reviews_elem = item.find("span", {"class": "a-size-base", "aria-label": True})
            if reviews_elem:
                reviews_text = reviews_elem["aria-label"]
                reviews = int(reviews_text.split()[0].replace(",", "")) if "ratings" in reviews_text else 0

            products.append({
                "Name": name,
                "Price": price,
                "Rating": rating,
                "Reviews": reviews,
                "Image": image_url,
                "Link": product_url,
                "Website": "amazon"
            })
        except (ValueError, AttributeError) as e:
            print(f"Error processing product: {e}")
            continue
    if not products:
        print("No products found. Possible issues: amazon")

    return products