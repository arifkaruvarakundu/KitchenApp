from django.urls import path
from .views import AddToCartView, CartDetailView


urlpatterns = [
    path('add_to_cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart_details/', CartDetailView.as_view(), name = 'cart-details')
   
]