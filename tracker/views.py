from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from forex_python.converter import CurrencyRates
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import ProductSearch, ProductResult
from .tasks import scrape_all_sites
import json
from datetime import datetime, timedelta
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import SignUpForm



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Sign up failed. Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'tracker/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Login failed. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def index(request):
    if request.method == 'POST':
        name = request.POST['product'].strip()
        target_price = float(request.POST['target'])
        
        # Check if similar active search exists
        existing_search = ProductSearch.objects.filter(
            user=request.user,
            name__iexact=name,
            is_active=True,
            last_checked__gte=datetime.now()-timedelta(hours=6)
        ).first()
        
        if existing_search:
            return redirect('results', search_id=existing_search.id)
        
        search = ProductSearch.objects.create(
            user=request.user,
            name=name,
            target_price=target_price
        )
        
        # Start async scraping
        scrape_all_sites.delay(search.id)
        
        return redirect('results', search_id=search.id)
    
    recent_searches = ProductSearch.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'tracker/index.html', {'recent_searches': recent_searches})


@login_required
def results(request, search_id):
    search = get_object_or_404(ProductSearch, id=search_id, user=request.user)
    results = ProductResult.objects.filter(search=search).order_by('price')
    
    # Check for price alerts
    lowest_price = results.first().price if results.exists() else None
    if lowest_price and lowest_price <= search.target_price:
        send_price_alert(request.user.email, search, lowest_price)
    
    return render(request, 'tracker/results.html', {
        'search': search,
        'results': results,
        'best_deal': results.first() if results.exists() else None
    })

@login_required
def price_chart_view(request, search_id):
    search = get_object_or_404(ProductSearch, id=search_id, user=request.user)
    results = ProductResult.objects.filter(search=search).order_by('timestamp')
    
    # Prepare chart data
    chart_data = prepare_chart_data(results, search.target_price)
    
    return render(request, 'tracker/chart.html', {
        'product_name': search.name,
        'target_price': search.target_price,
        'chart_data': json.dumps(chart_data),
        'search_id': search_id
    })

@login_required
def send_price_alert(email, search, current_price):
    subject = f"Price Alert: {search.name} dropped to {current_price} BDT!"
    message = (
        f"Your tracked product '{search.name}' has reached your target price!\n\n"
        f"Current Price: {current_price} BDT\n"
        f"Your Target: {search.target_price} BDT\n\n"
        f"View details: {settings.SITE_URL}/results/{search.id}"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

@login_required
def prepare_chart_data(results, target_price):
    # Group by site and prepare datasets
    sites = {}
    for result in results:
        if result.site not in sites:
            sites[result.site] = []
        sites[result.site].append({
            'x': result.timestamp.strftime('%Y-%m-%d %H:%M'),
            'y': result.price,
            'in_stock': result.in_stock
        })
    
    # Create datasets for Chart.js
    datasets = []
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
    
    for i, (site, data) in enumerate(sites.items()):
        datasets.append({
            'label': site,
            'data': data,
            'borderColor': colors[i % len(colors)],
            'backgroundColor': 'transparent',
            'pointRadius': 5,
            'pointBackgroundColor': [
                '#2ecc71' if point['in_stock'] else '#e74c3c' for point in data
            ],
            'borderWidth': 2,
            'tension': 0.1
        })
    
    # Add target price line
    if results.exists():
        timestamps = sorted({point['x'] for data in sites.values() for point in data})
        datasets.append({
            'label': 'Target Price',
            'data': [{'x': ts, 'y': target_price} for ts in timestamps],
            'borderColor': '#ff0000',
            'borderWidth': 1,
            'borderDash': [5, 5],
            'pointRadius': 0,
            'fill': False
        })
    
    return {
        'datasets': datasets,
        'min_price': min(r.price for r in results) if results else 0,
        'max_price': max(r.price for r in results) if results else target_price*1.5
    }

def convert_to_bdt(price, currency):
    if currency == 'BDT':
        return price
    try:
        c = CurrencyRates()
        return price * c.get_rate(currency, 'BDT')
    except:
        # Fallback conversion rates if API fails
        rates = {
            'USD': 105.0,  # 1 USD = 105 BDT (example rate)
            'EUR': 120.0,  # 1 EUR = 120 BDT
            'GBP': 140.0,  # 1 GBP = 140 BDT
            'CNY': 15.0    # 1 CNY = 15 BDT
        }
        return price * rates.get(currency, 1)