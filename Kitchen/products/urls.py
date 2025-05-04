from django.urls import path
from .views import AllProductsView, AllProductsCategoryView, ProductDetailView

urlpatterns = [
    path('products/', AllProductsView.as_view(), name='all-products'),
    path('categories/', AllProductsCategoryView.as_view(), name='all-products-category'),
    path('products/<str:category_slug>/<str:product_slug>/', ProductDetailView.as_view(), name='product_detail'),

]