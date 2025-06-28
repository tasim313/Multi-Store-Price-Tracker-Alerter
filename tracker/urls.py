from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chart/<int:search_id>/', views.price_chart_view, name='price_chart'),
]
