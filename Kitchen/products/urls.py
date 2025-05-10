from django.urls import path
from .views import AllProductsView, AllProductsCategoryView, ProductDetailView, SearchProductsView

urlpatterns = [
    path('products/', AllProductsView.as_view(), name='all-products'),
    path('categories/', AllProductsCategoryView.as_view(), name='all-products-category'),
    path('product_details/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('search/', SearchProductsView.as_view(), name='search-products'),

]