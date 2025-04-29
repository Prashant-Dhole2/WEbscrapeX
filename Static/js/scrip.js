function fetchPrice() {
    const url = document.getElementById("productUrl").value;
    fetch("/fetch-price", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("priceResult").innerText = "Price: " + data.price;
    })
    .catch(error => console.error("Error fetching price:", error));
}
