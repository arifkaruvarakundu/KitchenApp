from django.shortcuts import render
# Create your views here.
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Order, OrderItem
from .serializers import OrderListSerializer, OrderDetailSerializer
from authentication.models import User, Address
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.crypto import get_random_string
from rest_framework import status
from products.models import ProductVariant
from cart.models import Cart, CartItem
from django.db import transaction
from django.shortcuts import get_object_or_404

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
                cart.delete()

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