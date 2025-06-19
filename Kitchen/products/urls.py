from django.urls import path
from .views import *

urlpatterns = [
    path('products/', AllProductsView.as_view(), name='all-products'),
    path('categories/', AllProductsCategoryView.as_view(), name='all-products-category'),
    path('product_details/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('search/', SearchProductsView.as_view(), name='search-products'),
    path('addproduct/', AddProductView.as_view(), name='add-product'),
    path('deleteproduct/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
    path('editproduct/<int:pk>/', EditProductView.as_view(), name='edit-product'),
    path('addcategory/', AddCategoryView.as_view(), name = 'add-category'),
    path('deletecategory/<int:pk>/', DeleteCategoryView.as_view(), name = 'delete-category'),
    path('category_details/<int:pk>/', CategoryDetailView.as_view(), name = 'category-details'),
    path('editcategory/<int:id>/', EditCategoryView.as_view(), name='edit-category'),

]