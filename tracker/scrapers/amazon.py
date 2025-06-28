import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re

def search_product(product_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    # Amazon US search URL
    search_url = f"https://www.amazon.com/s?k={quote(product_name)}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find first product result
        product = soup.find('div', {'data-component-type': 's-search-result'})
        if not product:
            return None
        
        # Extract title
        title_elem = product.find('h2')
        title = title_elem.text.strip() if title_elem else "No title"
        
        # Extract price - handling different price formats
        price_whole = product.find('span', {'class': 'a-price-whole'})
        price_fraction = product.find('span', {'class': 'a-price-fraction'})
        
        if price_whole and price_fraction:
            price_text = f"{price_whole.text.strip()}{price_fraction.text.strip()}"
        else:
            price_text = product.find('span', {'class': 'a-offscreen'})
            price_text = price_text.text.strip() if price_text else "0"
        
        price = float(re.sub(r'[^\d.]', '', price_text))
        
        # Extract URL
        relative_url = product.find('a', {'class': 'a-link-normal'})['href']
        url = f"https://www.amazon.com{relative_url.split('?')[0]}"
        
        # Check stock status
        stock_elem = product.find('span', {'class': 'a-color-success'})
        in_stock = bool(stock_elem and "in stock" in stock_elem.text.lower())
        
        return {
            'site': 'Amazon',
            'title': title,
            'price': price,
            'url': url,
            'in_stock': in_stock,
            'currency': 'USD'
        }
        
    except Exception as e:
        print(f"Error scraping Amazon: {e}")
        return None