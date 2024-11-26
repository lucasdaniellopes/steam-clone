from django.urls import path
from .views import HomeView, AboutView, SearchView, SearchByCategoryView

urlpatterns = [
    path('home', HomeView.as_view(), name='home'),
    path('about', AboutView.as_view(), name='about'),
    path('search', SearchView.as_view(), name='search'),
    path('searchByCategory', SearchByCategoryView.as_view(), name='searchByCategory'),
]
