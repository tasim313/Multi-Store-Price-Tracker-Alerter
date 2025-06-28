from celery import shared_task
from .models import ProductSearch, ProductResult
from .scrapers import (
    daraz, startech, ryans, 
    pickaboo, gadget_and_gear,
    amazon, ebay, alibaba, aliexpress
)
import time

@shared_task(bind=True)
def scrape_all_sites(self, search_id):
    search = ProductSearch.objects.get(id=search_id)
    scrapers = [
        daraz, startech, ryans,
        pickaboo, gadget_and_gear,
        amazon, ebay, alibaba, aliexpress
    ]
    
    results = []
    for scraper in scrapers:
        try:
            data = scraper.search_product(search.name)
            if data and data['price'] > 0:  # Filter invalid prices
                result = ProductResult.objects.create(
                    search=search,
                    site=data['site'],
                    title=data['title'],
                    price=data['price'],
                    url=data['url'],
                    in_stock=data.get('in_stock', True)
                )
                results.append(result)
                # Avoid rate limiting
                time.sleep(1)
        except Exception as e:
            continue
    
    return len(results)