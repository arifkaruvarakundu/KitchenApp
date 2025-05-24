from django.urls import path
from .views import *

urlpatterns = [
    path('place_order/', PlaceOrderView.as_view(), name= 'place-order' ),
    path('user_orders/', UserOrdersView.as_view(), name='user-orders'),
    path('order_details/<int:order_id>/', OrderDetailsView.as_view(), name = 'order-details'),

    # path('wholesaler/orders/', WholesalerOrdersView.as_view(), name='wholesaler-orders'),
    # path('advance_payment/', AdvancePaymentView.as_view(), name='create_payment'),
    # path('notifications/', NotificationListView.as_view(), name='notification-list'),
    # path('notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]