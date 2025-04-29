import requests
from bs4 import BeautifulSoup

def scrape_reliance(product):
    query = product.replace(" ", "+")
    url = f"https://www.reliancedigital.in/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Reliance Digital page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    seen = set()

    for item in soup.select("li.grid"):
        name_elem = item.find("p", class_="sp__name")
        price_elem = item.find("span", class_="TextWeb__Text-sc-1cyx778-0")
        image_elem = item.find("img")
        link_elem = item.find("a", href=True)

        if not all([name_elem, price_elem, image_elem, link_elem]):
            continue

        try:
            name = name_elem.text.strip()
            price_text = price_elem.text.replace("₹", "").replace(",", "").strip()
            price = float(price_text) if price_text else 0.0
            image_url = image_elem["src"]

            # Updated URL logic
            product_url = "https://www.reliancedigital.in" + link_elem["href"] if link_elem["href"].startswith("/") else link_elem["href"]

            product_id = f"{name[:50]}-{price}"
            if product_id in seen:
                continue
            seen.add(product_id)

            products.append({
                "Name": name,
                "Price": price,
                "Rating": None,
                "Reviews": None,
                "Image": image_url,
                "Link": product_url,
                "Website": "Reliance Digital"
            })
        except Exception as e:
            print(f"Error processing Reliance product: {e}")
            continue

    if not products:
        print("No products found on Reliance Digital.")

    return products
