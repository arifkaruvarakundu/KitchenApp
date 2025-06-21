from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import *
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.conf import settings
import logging
from django.core.files.uploadedfile import InMemoryUploadedFile
import json, traceback, decimal, cloudinary.uploader
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import parsers
from collections import defaultdict
import re
import decimal
from decimal import Decimal, InvalidOperation
from .utils import upload, destroy
from django.shortcuts import get_object_or_404

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
            products = Product.objects.filter(is_active=True)
            serializer = ProductListSerializer(products, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AdminAllProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        This endpoint retrieves all products from the database.
        """
        try:
            products = Product.objects.all()
            serializer = ProductListSerializer(products, many=True, context={'request': request})
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

class AddProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            category_id = data.get("category")

            if not category_id:
                return Response({"error": "Category ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                category = ProductCategory.objects.get(id=category_id)
            except ProductCategory.DoesNotExist:
                return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.create(
                product_name_en=data.get("product_name_en"),
                product_name_ar=data.get("product_name_ar"),
                description_en=data.get("description_en"),
                description_ar=data.get("description_ar"),
                use_and_care_en=data.get("use_and_care_en"),
                use_and_care_ar=data.get("use_and_care_ar"),
                category=category,
            )

            # Step 2: Extract variants manually
            variants = defaultdict(dict)
            for key in data:
                match = re.match(r"variants\[(\d+)\]\[(\w+)\]", key)
                if match:
                    index, field = int(match.group(1)), match.group(2)
                    variants[index][field] = data.get(key)

            # Identify default variant index
            default_variant_index = next(
                (i for i, v in variants.items() if v.get("is_default") == "true"), None
            )

            # Convert to sorted list
            variant_list = [variants[i] for i in sorted(variants)]

            for index, variant_data in enumerate(variant_list):
                is_default_variant = (index == default_variant_index)
                default_new_image_index = variant_data.get("default_image_index")
                default_existing_image_index = variant_data.get("default_existing_image_index")

                # Create variant
                variant = ProductVariant.objects.create(
                    product=product,
                    color=variant_data.get("color_en"),
                    color_ar=variant_data.get("color_ar"),
                    price=decimal.Decimal(variant_data.get("price") or 0),
                    stock=int(variant_data.get("stock") or 0),
                    discount_percentage=decimal.Decimal(variant_data.get("discount_percentage") or 0),
                    is_default=is_default_variant,
                )

                # Upload new images
                for img_idx, image_file in enumerate(request.FILES.getlist(f"variants[{index}][images][]")):
                    try:
                        upload_result = cloudinary.uploader.upload(image_file)
                        ProductVariantImage.objects.create(
                            variant=variant,
                            product=product,
                            image=upload_result["public_id"],
                            public_id=upload_result["public_id"],
                            is_default=(str(img_idx) == str(default_new_image_index))
                        )
                    except Exception as e:
                        return Response({"error": f"Cloudinary upload failed: {str(e)}"}, status=400)

                # TODO: Handle existing images (edit case)

            return Response({"message": "Product and variants added successfully"}, status=status.HTTP_201_CREATED)

        except ProductCategory.DoesNotExist:
            return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteProductView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
      
        try:
            product = Product.objects.get(pk=pk)

            # Delete associated Cloudinary images
            for variant in product.variants.all():
                for image in variant.variant_images.all():  # 🔧 FIXED here
                    try:
                        if image.public_id:
                            cloudinary.uploader.destroy(image.public_id)
                    except Exception as e:
                        print(f"Cloudinary image delete failed: {e}")

            product.delete()  # will cascade delete due to on_delete=models.CASCADE
            return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EditProductView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def put(self, request, pk, *args, **kwargs):
        
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update product details
        product.product_name = request.data.get("product_name", product.product_name)
        product.product_name_ar = request.data.get("product_name_ar", product.product_name_ar)
        product.description = request.data.get("description", product.description)
        product.description_ar = request.data.get("description_ar", product.description_ar)
        product.use_and_care = request.data.get("use_and_care", product.use_and_care)
        product.use_and_care_ar = request.data.get("use_and_care_ar", product.use_and_care_ar)
        
        def parse_bool(val, default):
            if val is None:
                return default
            if isinstance(val, bool):
                return val
            return str(val).lower() in ["true", "1", "yes"]

        product.is_active = parse_bool(request.data.get("is_active"), product.is_active)

        # Update category
        category_id = request.data.get("category")
        if category_id:
            try:
                category = ProductCategory.objects.get(id=category_id)
                product.category = category
            except ProductCategory.DoesNotExist:
                return Response({"detail": "Invalid category ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Process variants
        variants_data = request.data.get("variants", [])

        if isinstance(variants_data, str):
            try:
                variants_data = json.loads(variants_data)
            except json.JSONDecodeError:
                return Response({"detail": "Invalid variants data format."}, status=status.HTTP_400_BAD_REQUEST)

        # Track existing variant IDs
        existing_variant_ids = {variant.id for variant in product.variants.all()}

        def parse_decimal(value):
            try:
                return Decimal(value) if value not in [None, "", "null"] else None
            except InvalidOperation:
                return None

        # Track default variant
        default_variant_id = None

        # Process each variant sent from the frontend
        for variant_index, variant_data in enumerate(variants_data):
            variant_id = variant_data.get("id")
            is_default_variant = variant_data.get("is_default", False)

            if variant_id and int(variant_id) in existing_variant_ids:
                # Update existing variant
                variant = ProductVariant.objects.get(id=int(variant_id))
                existing_variant_ids.remove(int(variant_id))  # Mark as updated
            else:
                # Create new variant
                variant = ProductVariant.objects.create(
                    product=product,
                    # brand=variant_data.get("brand", ""),
                    color=variant_data.get("color", ""),
                    color_ar=variant_data.get("color_ar", ""),
                    price=parse_decimal(variant_data.get("price")),
                    stock=parse_decimal(variant_data.get("stock")),
                    discount_percentage=parse_decimal(variant_data.get("discount_percentage")),
                )

            # Update variant fields (for both new and existing variants)
            # variant.brand = variant_data.get("brand", variant.brand)
            variant.color = variant_data.get("color", variant.color)
            variant.color_ar = variant_data.get("color_ar", variant.color_ar)
            variant.price = parse_decimal(variant_data.get("price"))
            variant.stock = parse_decimal(variant_data.get("stock"))
            variant.discount_percentage = parse_decimal(variant_data.get("discount_percentage"))
            variant.save()

            if is_default_variant:
                default_variant_id = variant.id

            # Set only one variant as default
            if default_variant_id:
                ProductVariant.objects.filter(product=product).update(is_default=False)
                ProductVariant.objects.filter(id=default_variant_id).update(is_default=True)


            # Handle images marked for deletion
            images_to_delete = variant_data.get("imagesToDelete", [])
            for image_id in images_to_delete:
                try:
                    image = ProductVariantImage.objects.get(id=image_id)
                    destroy(image.public_id)  # Delete from Cloudinary
                    image.delete()  # Remove from database
                except ProductVariantImage.DoesNotExist:
                    pass  # Ignore if the image doesn't exist

            # ✅ Handle existing image defaults
            existing_images = variant_data.get("existingImages", [])
            for img_data in existing_images:
                try:
                    img = ProductVariantImage.objects.get(id=img_data["id"])
                    is_default = img_data.get("is_default", False)

                    if is_default:
                        ProductVariantImage.objects.filter(
                            variant=variant, is_default=True
                        ).exclude(id=img.id).update(is_default=False)

                    img.is_default = is_default
                    img.save()
                except ProductVariantImage.DoesNotExist:
                    pass

            # Handle new images
            variant_files_key = f"new_images_{variant_index}_"
            for key, image_file in request.FILES.items():
                if key.startswith(variant_files_key):
                    uploaded_image = upload(image_file)
                    ProductVariantImage.objects.create(
                        product=product,
                        variant=variant,
                        image=uploaded_image["public_id"],
                        public_id=uploaded_image["public_id"],
                    )

        # Delete variants that were not included in the request
        for old_variant in product.variants.filter(id__in=existing_variant_ids):
            for image in old_variant.variant_images.all():
                destroy(image.public_id)  # Delete from Cloudinary
                image.delete()
            old_variant.delete()

        # Save product
        product.save()

        return Response({"detail": "Product updated successfully!"}, status=status.HTTP_200_OK)

class AddCategoryView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        category_name_en = request.data.get("category_name_en")
        category_name_ar = request.data.get("category_name_ar")
        category_image = request.FILES.get("category_image")  # Optional

        if not category_name_en or not category_name_ar:
            return Response({"detail": "Both English and Arabic category names are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Optional: Validate if same Arabic or English names exist
        if ProductCategory.objects.filter(category_name_en=category_name_en).exists():
            return Response({"detail": "Category name (EN) already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if ProductCategory.objects.filter(category_name_ar=category_name_ar).exists():
            return Response({"detail": "Category name (AR) already exists."}, status=status.HTTP_400_BAD_REQUEST)

        category = ProductCategory.objects.create(
            category_name_en=category_name_en,
            category_name_ar=category_name_ar,
            category_image=category_image,
            slug=slugify(category_name_en),
        )

        return Response({"detail": "Category created successfully!", "id": category.id}, status=status.HTTP_201_CREATED)

class DeleteCategoryView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            category = ProductCategory.objects.get(pk=pk)
            category.delete()
            return Response({"detail": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ProductCategory.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

class CategoryDetailView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, pk, *args, **kwargs):
        category = get_object_or_404(ProductCategory, pk=pk)
        serializer = ProductCategorySerializer(category, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EditCategoryView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, id):
        category = get_object_or_404(ProductCategory, pk=id)
        serializer = ProductCategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, id):
        category = get_object_or_404(ProductCategory, pk=id)
        serializer = ProductCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Category updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)