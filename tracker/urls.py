from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('chart/<int:search_id>/', views.price_chart_view, name='price_chart'),
    path('results/<int:search_id>/', views.results, name='results'), 
    path('', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
