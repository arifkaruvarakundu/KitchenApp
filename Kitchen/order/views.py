from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import *
from .serializers import *
from authentication.models import User, Address
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.crypto import get_random_string
from rest_framework import status
from products.models import ProductVariant
from cart.models import Cart, CartItem
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import generics
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import Http404
from django.http import FileResponse
from django.utils.dateparse import parse_date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# Create your views here.

class PlaceOrderView(APIView):

    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user, is_active=True)
            cart_items = cart.items.select_related('variant')

            if not cart_items.exists():
                return Response({'error': 'Cart is empty'}, status=400)

            # Begin atomic transaction
            with transaction.atomic():
                # Check stock availability
                for item in cart_items:
                    if item.variant and item.quantity > item.variant.stock:
                        return Response({
                            'error': f"Insufficient stock for {item.product.product_name} (variant: {item.variant.id})"
                        }, status=400)

                # Create Order
                order = Order.objects.create(user=user)  # Fill in with required fields

                # Example logic: add items to order and reduce stock
                for item in cart_items:
                    variant = item.variant
                    if variant:
                        # Deduct stock
                        variant.stock -= item.quantity
                        if variant.stock <= 0:
                            variant.is_available = False
                        variant.save()

                    # Add item to order (adjust as needed)
                    order.items.create(
                        product_variant=variant,
                        quantity=item.quantity
                    )

                # Delete cart items and cart
                cart_items.delete()
                # cart.delete()

                return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({'error': 'Active cart not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
    
        # Get all orders for the current user
        orders = Order.objects.filter(user=request.user)
    
        # Serialize the orders and campaign orders
        order_serializer = OrderListSerializer(orders, many=True)
      
        return Response({
            'orders': order_serializer.data,
        
        })

class OrderDetailsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class InvoiceDetailView(generics.ListAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all notifications for the authenticated user
        notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Mark a specific notification as read
        notification = Notification.objects.get(id=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"status": "success"})

class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        orders_count = Order.objects.filter(user=user).count()
        unread_notifications_count = user.notifications.filter(is_read=False).count()

        return Response({
            'orders_count': orders_count,
            'unread_notifications_count': unread_notifications_count,
        })

class AdminOrderDetailsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EditOrderView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderDetailSerializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteOrderView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response({"detail":"Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

class InvoiceDownloadView(APIView):
    
    def get(self, request, order_id):
        try:
            order = Order.objects.select_related('user').get(id=order_id)
        except Order.DoesNotExist:
            raise Http404("Order not found.")

        invoice = order.invoice  # assuming OneToOneField

        # Get the first address if available
        addresses = order.user.addresses.all()
        address = addresses[0] if addresses else None

        html_string = render_to_string('invoices/invoice_template.html', {
            'order': order,
            'invoice': invoice,
            'address': address,  # pass the address separately
        })

        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=invoice_{order_id}.pdf'
        return response
    
class SalesReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = request.query_params.get('start_date')
        end = request.query_params.get('end_date')

        if not start or not end:
            return Response({"error": "start_date and end_date are required."}, status=400)

        try:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date > end_date:
                return Response({"error": "start_date must be before end_date."}, status=400)
        except Exception:
            return Response({"error": "Invalid date format."}, status=400)

        orders = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

        # Prepare data for template
        order_data = []
        total_sum = 0

        for order in orders:
            total = order.total_amount()
            total_sum += total
            order_data.append({
                'id': order.id,
                'date': order.created_at.strftime('%Y-%m-%d'),
                'customer': f"{order.user.first_name} {order.user.last_name}",
                'total': f"{total:.2f}",
                'status': order.status
            })

        context = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'generation_date': timezone.now().strftime('%Y-%m-%d'),
            'orders': order_data,
            'total_sales': f"{total_sum:.2f}",
        }

        html_string = render_to_string('reports/sales_report.html', context)
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="sales_report.pdf"'
        return response
    
class FilterOrdersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("DEBUG: Using the correct FilterOrdersView.get() method.")
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        orders = Order.objects.all()

        if start_date and end_date:
            try:
                start = parse_date(start_date)
                end = parse_date(end_date)
                if start and end:
                    orders = orders.filter(created_at__date__gte=start, created_at__date__lte=end)
            except Exception as e:
                return Response({"error": "Invalid date format."}, status=400)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)