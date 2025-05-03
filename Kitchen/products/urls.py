from django.urls import path
from .views import AllProductsView, AllProductsCategoryView

urlpatterns = [
    path('products/', AllProductsView.as_view(), name='all-products'),
    path('categories/', AllProductsCategoryView.as_view(), name='all-products-category'),

]