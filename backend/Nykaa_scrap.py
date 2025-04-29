import requests
from bs4 import BeautifulSoup
def scrape_nykaa(product): 

    url = f"https://www.nykaa.com/search/result/?q={product.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Nykaa page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    for item in soup.find_all("a", class_="css-qlopj4"):
        try:
            name = item.find("div", class_="css-xrzmfa").text.strip()
            price_elem = item.find("span", class_="css-111z9ua")
            price = float(price_elem.text.replace("₹", "").replace(",", "").strip()) if price_elem else 0.0
            image = item.find("img")["src"]
            link = "https://www.nykaa.com" + item["href"]

            
            # Review data
            review_text = item.find("div", class_="css-1n7v3ny")
            rating = 0.0
            reviews = 0

            if review_text:
                text = review_text.text.strip()
                if "/" in text:
                    rating = float(text.split("/")[0])
                if "Ratings" in text or "ratings" in text:
                    reviews = int(''.join(filter(str.isdigit, text.split()[-2])))  # Approx logic


            products.append({ 
                "Name": name,
                "Price": price,
                "Rating": rating,
                "Reviews": reviews,
                "Image": image,
                "Link": link,
                "Website": "nykaa"
            })
        except Exception as e:
            print(f"Nykaa error: {e}")
            continue

    if not products:
        print("Nykaa: No products found.")
    return products
