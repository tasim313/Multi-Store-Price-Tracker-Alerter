from django import template
from forex_python.converter import CurrencyRates

register = template.Library()

@register.filter
def convert_to_bdt(price, currency='USD'):
    if currency == 'BDT':
        return price
    try:
        c = CurrencyRates()
        return round(price * c.get_rate(currency, 'BDT'), 2)
    except:
        rates = {
            'USD': 105.0,
            'EUR': 120.0,
            'GBP': 140.0,
            'CNY': 15.0
        }
        return round(price * rates.get(currency, 1), 2)