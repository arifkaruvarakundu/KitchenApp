from django.urls import path
from .views import *

urlpatterns = [
    path('place_order/', PlaceOrderView.as_view(), name= 'place-order' ),
    path('user_orders/', UserOrdersView.as_view(), name='user-orders'),
    path('order_details/<int:order_id>/', OrderDetailsView.as_view(), name = 'order-details'),
    path('Invoice/<int:order_id>/', InvoiceViewSet.as_view(), name='invoice'),

]