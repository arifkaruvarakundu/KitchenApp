from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from products.models import Product, ProductVariant  # adjust import based on your project structure
import uuid

class AddToCartView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))
        cart_uuid = request.data.get('cart_uuid')

        if not product_id:
            return Response({"error": "product_id is required"}, status=400)

        product = get_object_or_404(Product, id=product_id)
        variant = None

        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

        # Get or create the cart
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        elif cart_uuid:
            cart, _ = Cart.objects.get_or_create(uuid=cart_uuid, is_active=True)
        else:
            cart = Cart.objects.create()

        # Add item to cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        # Set price from variant if available, else base product price
        if variant and variant.price:
            cart_item.price = variant.price
        else:
            cart_item.price = product.price

        cart_item.save()

        return Response({
            "message": "Item added to cart",
            "cart_uuid": str(cart.uuid),
            "item_id": cart_item.id,
            "variant": {
                "id": variant.id,
                "color": variant.color,
                "size": variant.size,
                "price": str(variant.price)
            } if variant else None
        }, status=status.HTTP_200_OK)

class CartDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cart_uuid = request.query_params.get('cart_uuid')

        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
        elif cart_uuid:
            cart = Cart.objects.filter(uuid=cart_uuid, is_active=True).first()
        else:
            return Response({"items": []}, status=200)

        if not cart:
            return Response({"items": []}, status=200)

        items = CartItem.objects.filter(cart=cart).select_related('product', 'variant')

        serialized_items = []
        for item in items:
            serialized_items.append({
                "id": item.id,
                "product_id": item.product.id,
                "name": item.product.product_name,
                "quantity": item.quantity,
                "price": str(item.price),
                "variant": {
                    "id": item.variant.id if item.variant else None,
                    "color": item.variant.color if item.variant else None,
                    "size": item.variant.size if item.variant else None
                },
                "image": item.variant.variant_images.first().image.url if item.variant and item.variant.variant_images.exists() else None
            })

        return Response({"items": serialized_items}, status=200)