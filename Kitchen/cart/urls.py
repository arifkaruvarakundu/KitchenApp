from django.urls import path
from .views import *


urlpatterns = [
    path('add_to_cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart_details/', CartDetailView.as_view(), name = 'cart-details'),
    path('remove_from_cart/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('merge_guest_cart/', MergeGuestCartView.as_view(), name = 'merge-guest-cart'),
    path('has_user_cart/', HasUserCartView.as_view(), name='has_user_cart'),
   
]