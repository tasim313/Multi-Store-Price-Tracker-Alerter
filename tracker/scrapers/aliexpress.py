import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re

def search_product(product_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    # AliExpress search URL
    search_url = f"https://www.aliexpress.com/wholesale?SearchText={quote(product_name)}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find first product card
        product = soup.find('div', {'class': 'product-container'})
        if not product:
            return None
        
        # Extract title
        title_elem = product.find('h1', {'class': 'item-title'})
        title = title_elem.text.strip() if title_elem else "No title"
        
        # Extract price
        price_elem = product.find('span', {'class': 'price-current'})
        price_text = price_elem.text.strip() if price_elem else "0"
        
        # Handle price ranges like "$12.00 - $15.00"
        if '-' in price_text:
            price_text = price_text.split('-')[0].strip()
        
        price = float(re.sub(r'[^\d.]', '', price_text))
        
        # Extract URL
        relative_url = product.find('a')['href']
        url = f"https:{relative_url}" if relative_url.startswith('//') else relative_url
        
        # Check stock status (AliExpress usually shows items as available)
        in_stock = True
        
        return {
            'site': 'AliExpress',
            'title': title,
            'price': price,
            'url': url,
            'in_stock': in_stock,
            'currency': 'USD'
        }
        
    except Exception as e:
        print(f"Error scraping AliExpress: {e}")
        return None