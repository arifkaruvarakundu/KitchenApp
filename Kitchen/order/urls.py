from django.urls import path
from .views import *

urlpatterns = [
    path('place_order/', PlaceOrderView.as_view(), name= 'place-order' ),
    path('orders/', OrderListView.as_view(), name='orders'  ),
    path('user_orders/', UserOrdersView.as_view(), name='user-orders'),
    path('order_details/<int:order_id>/', OrderDetailsView.as_view(), name = 'order-details'),
    path('Invoice/<int:order_id>/', InvoiceDetailView.as_view(), name='invoice'),
    path('admin_order_details/<int:order_id>/', AdminOrderDetailsView.as_view(), name='admin-order-details'),
    path('edit_order/<int:order_id>/', EditOrderView.as_view(), name='edit-order'),
    path('delete_order/<int:pk>/', DeleteOrderView.as_view(), name='delete-order'),
    path('invoice/download/<int:order_id>/', InvoiceDownloadView.as_view(), name='download_invoice'),
    path('sales-report/', SalesReportPDFView.as_view(), name='sales-report'),
    path('orders/filter/', FilterOrdersView.as_view(), name='filtered-orders'),
    path('user_stats/', UserStatsView.as_view(), name='user-stats'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),


]