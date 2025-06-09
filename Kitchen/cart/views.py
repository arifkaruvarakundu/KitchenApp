from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from products.models import Product, ProductVariant  # adjust import based on your project structure
import uuid

# Create your views here.
class AddToCartView(APIView):
    
    permission_classes = [AllowAny]

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

class RemoveFromCartView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request):
        user = request.user if request.user.is_authenticated else None
        variant_id = request.data.get('variant_id')
      
        if not variant_id:
            return Response({"error": "variant_id is required"}, status=400)

        try:
            variant_id = int(variant_id)
        except (ValueError, TypeError):
            return Response({"error": "Invalid variant_id"}, status=400)

        try:
            print("User:", user)
            print("Is authenticated:", user.is_authenticated if user else False)

            if user:
                # Remove item from authenticated user's cart
                cart_item = CartItem.objects.get(cart__user=user, variant_id=variant_id)
            else:
                # Handle guest users via cart_uuid in session/cookie
                cart_uuid = request.data.get('cart_uuid')
                cart_item = CartItem.objects.get(cart__uuid=cart_uuid, variant_id=variant_id)

            cart_item.delete()
            return Response({"success": True}, status=200)

        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=404)

class MergeGuestCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        guest_cart_uuid = request.data.get("cart_uuid")
        if not guest_cart_uuid:
            return Response({"error": "cart_uuid is required"}, status=400)

        try:
            guest_cart = Cart.objects.get(uuid=guest_cart_uuid, user__isnull=True)
            user_cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)

            # Move items from guest cart to user's cart
            for item in guest_cart.items.all():
                user_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=item.product,
                    variant=item.variant,
                    defaults={
                        "quantity": item.quantity,
                        "price": item.price,
                    }
                )
                if not created:
                    user_item.quantity += item.quantity
                    user_item.save()

            guest_cart.delete()  # optional: clean up guest cart

            return Response({"message": "Cart merged successfully"}, status=200)

        except Cart.DoesNotExist:
            return Response({"error": "Guest cart not found"}, status=404)

class HasUserCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        has_cart = Cart.objects.filter(user=request.user, is_active=True).exists()
        return Response({"has_cart": has_cart})