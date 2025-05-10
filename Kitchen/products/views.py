from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer, ProductCategorySerializer
from rest_framework.permissions import AllowAny
from .models import Product, ProductCategory
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.conf import settings
import logging
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

    def get(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.prefetch_related("variants__variant_images").get(pk=pk)  
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
# class ProductDetailView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, category_slug, product_slug, *args, **kwargs):
#         """
#         This endpoint retrieves a specific product by its slug.
#         """
#         try:
#             product = Product.objects.get(slug=product_slug, category__slug=category_slug)
#             serializer = ProductSerializer(product, context={'request': request})
#             return Response(serializer.data, status=status.HTTP_200_OK)
        
#         except Product.DoesNotExist:
#             return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
logger = logging.getLogger(__name__)

class SearchProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.GET.get('query', '').strip()

        if len(query) < 3:
            return Response({'products': [], 'categories': []}, status=status.HTTP_200_OK)

        try:
            # Define limits (configurable)
            product_limit = getattr(settings, 'SEARCH_PRODUCT_LIMIT', 10)
            category_limit = getattr(settings, 'SEARCH_CATEGORY_LIMIT', 5)

            # Full-text search (PostgreSQL)
            search_query = SearchQuery(query)

            products = Product.objects.annotate(
                rank=SearchRank(SearchVector('product_name', weight='A'), search_query)
            ).filter(rank__gte=0.1).order_by('-rank')[:product_limit]

            categories = ProductCategory.objects.filter(category_name__icontains=query)[:category_limit]

            return Response({
                'products': ProductSerializer(products, many=True).data,
                'categories': ProductCategorySerializer(categories, many=True).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error in product search")  # Log full traceback
            return Response(
                {"detail": "An error occurred while retrieving search results."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )