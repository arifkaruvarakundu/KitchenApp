from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer, ProductCategorySerializer, ProductFeatureSerializer, ProductVariantSerializer
from rest_framework.permissions import AllowAny
from .models import Product, ProductCategory, ProductFeature, ProductVariant

# Create your views here.

# class ProductCreateView(APIView):
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        This endpoint retrieves all products from the database.
        """
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AllProductsCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        """
        This endpoint retrieves all products category from the database.
        """

        try:
            categories = ProductCategory.objects.all()
            serializer = ProductCategorySerializer(categories, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_slug, product_slug, *args, **kwargs):
        """
        This endpoint retrieves a specific product by its slug.
        """
        try:
            product = Product.objects.get(slug=product_slug, category__slug=category_slug)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        