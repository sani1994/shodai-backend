from django.core.paginator import Paginator
from rest_framework.generics import get_object_or_404

from product.serializers import ShopCategorySerializer, ProductCategorySerializer, ProductSerializer, \
    ProductMetaSerializer, ProductForCartSerializer
from product.models import ShopCategory, ProductMeta, ProductCategory, Product
from utility.models import ProductUnit
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from shodai.permissions import GenericAuth


# class ProductList(APIView):
#     """Get all product and create a product"""
#     permission_classes = [GenericAuth]
#
#     def get(self, request, format=None):
#         products = Product.objects.filter(is_approved=True)
#         serializer = ProductSerializer(products, many=True)
#         if serializer:
#             datas = serializer.data
#
#             for data in range(len(datas)):
#                 datas[data]['product_unit'] = ProductUnit.objects.get(id=int(datas[data]['product_unit'])).product_unit
#                 datas[data]['product_meta'] = ProductMeta.objects.get(id=int(datas[data]['product_meta'])).name
#             return Response(datas, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def post(self, request, format=None):
#         if request.user.user_type == 'SF':
#             serializer = ProductSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(created_by=request.user)
#                 return Response(serializer.data, status.HTTP_202_ACCEPTED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductDetail(APIView):
    permission_classes = [GenericAuth]
    """
    Retrieve product by id with offer price and offer name
    """

    def get_product_object(self, id):
        obj = get_object_or_404(Product, id=id, is_approved=True)
        return obj

    def get(self, request, id):
        product = self.get_product_object(id)
        serializer = ProductSerializer(product)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, id, format=None):
    #     if request.user.user_type == 'SF':
    #         product = self.get_product_object(id)
    #         if request.data['product_price'] != product.product_price:
    #             product.product_last_price = product.product_price
    #         serializer = ProductSerializer(product, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save(modified_by=request.user)
    #             # print(serializer.data)
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    # def delete(self, request, id, format=None):
    #     if request.user.user_type == 'SF':
    #         product = self.get_product_object(id)
    #         product.delete()
    #         return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductMetaList(APIView):
    """Get all product meta and crete product meta"""
    permission_classes = [GenericAuth]

    # list of Product Meta (original product name with company name)

    def get(self, request, format=None):
        product_meta = ProductMeta.objects.filter(is_approved=True)
        serializer = ProductMetaSerializer(product_meta, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if request.user.user_type == 'SF':
            serializer = ProductMetaSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductMetaDetail(APIView):
    # this method don't work because couldn't update and retrieve object of product meta object
    """
    Retrieve, update and delete product meta
    """
    permission_classes = [GenericAuth]

    def get_productMeta_object(self, id):
        obj = ProductMeta.objects.get(id=id)
        return obj

    def get(self, request, id, format=None):
        product_meta = self.get_productMeta_object(id)
        if product_meta:
            serializer = ProductMetaSerializer(product_meta)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "Status": "No content",
            "details": "Rontent not available"
        }, status=status.HTTP_204_NO_CONTENT)

    # def put(self, request, id, format=None):
    #     if request.user.user_type == 'SF':
    #         product_meta = self.get_productMeta_object(id)
    #         serializer = ProductMetaSerializer(product_meta, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save(modified_by=request.user)
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
    #
    # def delete(self, request, id, format=None):
    #     if request.user.user_type == 'SF':
    #         product_meta = self.get_productMeta_object(id)
    #         product_meta.delete()
    #         return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductCategoryList(APIView):
    # list of Prodect category

    def get(self, request, format=None):
        product_catagory = ProductCategory.objects.filter(is_approved=True, parent=None)
        serializer = ProductCategorySerializer(product_catagory, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def post(self, request, format=None):
    #     if request.user.user_type == 'SF':
    #         serializer = ProductCategorySerializer(data=request.data, context={'request': request})
    #         if serializer:
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductCategoryDetail(APIView):
    permission_classes = [GenericAuth]
    """
    Retrieve, update and delete Orders
    """

    def get_productCategory_object(self, id):  # enable another parameter "request" when to access user
        obj = ProductCategory.objects.get(id=id)
        return obj

    def get(self, request, id, format=None):
        product_catagory = self.get_productCategory_object(id)
        if product_catagory:
            serializer = ProductCategorySerializer(product_catagory, context={'request': request})
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "Status": "No content",
            "details": "Content not available"
        }, status=status.HTTP_204_NO_CONTENT)

    # def put(self, request, id, format=None):
    #     if request.user.user_type == 'SF':
    #         product_catagory = self.get_productCategory_object(id)
    #         serializer = ProductCategorySerializer(product_catagory, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save(modified_by=request.user)
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
    #
    # def delete(self, request, id, format=None):
    #     if request.user.user_type == 'SF':
    #         product_catagory = self.get_productCategory_object(id)
    #         product_catagory.delete()
    #         return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ShopCategoryList(APIView):
    permission_classes = [GenericAuth]
    # shop_category must be in unique format to make the connection with shop model of retailer
    # list of Shop category

    def get(self, request, format=None):
        shop_catagory = ShopCategory.objects.filter(is_approved=True)
        serializer = ShopCategorySerializer(shop_catagory, many=True, context={'request': request})
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def post(self, request, format=None):
    #     if request.user.user_type == 'SF':
    #         serializer = ShopCategorySerializer(data=request.data)
    #         if serializer.is_valid():
    #             serializer.save(created_by=request.user)
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ShopCategoryDetail(APIView):  # to retrieve update and delete
    permission_classes = [GenericAuth]

    def get_shopCategory_object(self, id):
        obj = ShopCategory.objects.get(id=id)
        return obj

    def get(self, request, id, format=None):

        shop_catagory = self.get_shopCategory_object(id)
        print(shop_catagory)
        if shop_catagory:
            serializer = ShopCategorySerializer(shop_catagory, context={'request': request})
            print(serializer)
            if serializer:
                return Response(serializer.data)
            else:
                return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Rontent not available"
            }, status=status.HTTP_204_NO_CONTENT)

    # def put(self, request, id, format=None):
    #     if request.user.user_type == 'SF':
    #         shop_catagory = self.get_shopCategory_object(id)
    #         serializer = ShopCategorySerializer(shop_catagory, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save(modified_by=request.user)
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
    #
    # def delete(self, request, id, format=None):
    #     if request.user.user_type == 'SF':
    #         shop_catagory = self.get_shopCategory_object(id)
    #         shop_catagory.delete()
    #         return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
    #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductCategoryDetails(APIView):
    # get product category id to get all the product meta list related to that product category id

    permission_classes = [GenericAuth]

    def get(self, request, id):
        obj = ProductCategory.objects.filter(id=id, is_approved=True).first()
        if obj:
            all_subcategories = []
            subcategories = ProductCategory.objects.filter(parent=obj, is_approved=True)
            for category in subcategories:
                subcategory_data = {
                    "id": category.id,
                    "created_on": category.created_on,
                    "modified_on": category.modified_on,
                    "name": category.type_of_product,
                    "name_bn": "",
                    "img": category.img.url if category.img else "",
                    "vat_amount": 0.0,
                    "is_approved": True,
                    "code": None,
                    "created_by": 1,
                    "modified_by": 1,
                    "product_category": obj.id,
                    "shop_category": 1
                }
                all_subcategories.append(subcategory_data)
            return Response(all_subcategories, status=status.HTTP_200_OK)
            # productMetaList = obj.productmeta_set.filter(is_approved=True)
            # serializer = ProductMetaSerializer(productMetaList, many=True)
            # if serializer:
            #     return Response(serializer.data, status=status.HTTP_200_OK)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)


class ProductMetaDetails(APIView):  # get product meta id to get all the product list related to that product meta id

    permission_classes = [GenericAuth]

    def get(self, request, id):
        obj = ProductCategory.objects.filter(id=id, is_approved=True).first()
        if obj:
            productList = obj.product_set.filter(is_approved=True)
            serializer = ProductSerializer(productList, many=True)
            if serializer:
                datas = serializer.data
                for data in range(len(datas)):
                    datas[data]['product_unit'] = ProductUnit.objects.get(
                        id=int(datas[data]['product_unit'])).product_unit
                    # datas[data]['product_meta'] = ProductMeta.objects.get(id=int(datas[data]['product_meta'])).name

                return Response(datas, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)


class RecentlyAddedProductList(APIView):  # return list of recently added products
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = Product.objects.filter(is_approved=True).order_by('-created_on')[:200]
        serializer = ProductSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductForCart(APIView):
    permission_classes = [GenericAuth]
    """
    Retrieve products information to show in cart
    """

    def get_product_object(self, id):
        obj = get_object_or_404(Product, id=id, is_approved=True)
        return obj

    def get(self, request, id):
        product = self.get_product_object(id)
        serializer = ProductForCartSerializer(product)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecentlyAddedProductListPagination(APIView):
    permission_classes = [GenericAuth]

    def get(self, request, id):
        queryset = Product.objects.filter(is_approved=True).order_by('-created_on')
        paginator = Paginator(queryset, 10)  # Show 10 products per page
        products = paginator.get_page(id)
        serializer = ProductSerializer(products, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDescription(APIView):

    def get(self, request, id):
        product = get_object_or_404(Product, id=id, is_approved=True)
        return HttpResponse(content_type='text/html', content=product.product_description)


class ProductSearch(APIView):
    permission_classes = [GenericAuth]

    def get(self, request):
        query = request.query_params.get('search', '')
        product = Product.objects.filter(product_name__icontains=query, is_approved=True)[:20]
        serializer = ProductSerializer(product, many=True)
        if serializer:
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)