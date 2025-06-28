import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re

def search_product(product_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Search URL
    search_url = f"https://www.daraz.com.bd/catalog/?q={quote(product_name)}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find first product card
        product = soup.find('div', {'class': 'gridItem--Yd0sa'})
        if not product:
            return None
        
        # Extract details
        title = product.find('div', {'class': 'title--wFj93'}).text.strip()
        price_text = product.find('div', {'class': 'price--NVB62'}).text.strip()
        price = float(re.sub(r'[^\d.]', '', price_text))
        url = 'https:' + product.find('a')['href']
        
        # Check stock status
        stock_elem = product.find('div', {'class': 'quantity--hasBtn'})
        in_stock = stock_elem is not None
        
        return {
            'site': 'Daraz',
            'title': title,
            'price': price,
            'url': url,
            'in_stock': in_stock
        }
        
    except Exception as e:
        print(f"Error scraping Daraz: {e}")
        return None
