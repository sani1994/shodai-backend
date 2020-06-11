from django.shortcuts import render
from rest_framework.generics import get_object_or_404

import qrcode
from product.serializers import ShopCategorySerializer, ProductCategorySerializer, ProductSerializer, \
    ProductMetaSerializer, LatestProductSerializer
from product.models import ShopCategory, ProductMeta, ProductCategory, Product
from utility.models import ProductUnit
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from sodai.utils.permission import GenericAuth


class ProductList(APIView):
    # permission_classes = (IsAuthenticated,)

    # permission_classes = [GenericAuth]

    ## list of Prodect

    def get(self, request, format=None):
        products = Product.objects.filter(is_approved=True)
        serializer = ProductSerializer(products, many=True)
        if serializer:
            datas = serializer.data
       
            for data in range(len(datas)):
                datas[data]['product_unit'] = ProductUnit.objects.get(id=int(datas[data]['product_unit'])).product_unit
                datas[data]['product_meta'] = ProductMeta.objects.get(id=int(datas[data]['product_meta'])).name
            return Response(datas, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if request.user.user_type=='SF':
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data,status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductDetail(APIView):

    permission_classes = [GenericAuth]
    """
    Retrieve, update and delete Orders
    """

    def get_product_object(self,id):
        obj = get_object_or_404(Product,id=id)
        return obj

    def get(self, request,id):
        product = self.get_product_object(id)
        product_meta = product.product_meta
        serializer = ProductSerializer(product)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        if request.user.user_type=='SF':
            product = self.get_product_object(id)
            if request.data['product_price'] != product.product_price:
                product.product_last_price = product.product_price
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by = request.user)
                # print(serializer.data)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id, format=None):
        if request.user.user_type=='SF':
            product = self.get_product_object(id)
            product.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductMetaList(APIView):

    permission_classes = [GenericAuth]
    ## list of Prodect Meta (original product name with comapny name)

    def get(self, request, format=None):
        product_meta = ProductMeta.objects.all()
        serializer = ProductMetaSerializer(product_meta, many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if request.user.user_type=='SF':
            serializer = ProductMetaSerializer(data=request.data,context={'request':request})
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductMetaDetail(APIView):     # this mathod dont work because couldnt update and retriev object of productMea object
    """
    Retrieve, update and delete Orders
    """
    permission_classes = [GenericAuth]
    def get_productMeta_object(self,id):
        obj = ProductMeta.objects.get(id=id)
        return obj

    def get(self, request, id, format=None):
        product_meta = self.get_productMeta_object(id)
        if product_meta:
            serializer = ProductMetaSerializer(product_meta)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({
                "Status": "No content",
                "details": "Rontent not available"
                },status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id, format=None):
        if request.user.user_type=='SF':
            product_meta = self.get_productMeta_object(id)
            serializer = ProductMetaSerializer(product_meta, data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request, id, format=None):
        if request.user.user_type == 'SF':
            product_meta = self.get_productMeta_object(id)
            product_meta.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
    

class ProductCategoryList(APIView):
    ## list of Prodect category

    def get(self, request, format=None):
        product_catagory = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(product_catagory, many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if request.user.user_type=='SF':
            serializer = ProductCategorySerializer(data=request.data,context={'request': request})
            if serializer:
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductCategoryDetail(APIView):

    permission_classes = [GenericAuth]
    """
    Retrieve, update and delete Orders
    """

    def get_productCategory_object(self,id):     # enable another peremeter "request" when to access user
        obj = ProductCategory.objects.get(id=id)
        return obj

    def get(self, request, id,format=None):
        product_catagory = self.get_productCategory_object(id)
        if product_catagory:
            serializer = ProductCategorySerializer(product_catagory,context={'request':request})
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id, format=None):
        if request.user.user_type== 'SF':
            product_catagory = self.get_productCategory_object(id)
            serializer = ProductCategorySerializer(product_catagory, data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


    def delete(self,request, id, format=None):
        if request.user.user_type=='SF':
            product_catagory = self.get_productCategory_object(id)
            product_catagory.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ShopCategoryList(APIView):        # shop_category must be in unique formate to make the connection with shop model of retailer

    permission_classes = [GenericAuth]

    ## list of Shop category

    def get(self, request, format=None):
        shop_catagory = ShopCategory.objects.all()
        serializer = ShopCategorySerializer(shop_catagory, many=True,context={'request':request})
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if request.user.user_type== 'SF':
            serializer = ShopCategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ShopCategoryDetail(APIView):  # to retrive update and delete

    permission_classes = [GenericAuth]

    def get_shopCategory_object(self,id):
        obj = ShopCategory.objects.get(id=id)
        return obj

    def get(self,request,id, format=None):

        shop_catagory = self.get_shopCategory_object(id)
        print(shop_catagory)
        if shop_catagory:
            serializer = ShopCategorySerializer(shop_catagory,context={'request':request})
            print(serializer)
            if serializer:
                return Response(serializer.data)
            else:
                return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Rontent not available"
            }, status=status.HTTP_204_NO_CONTENT)


    def put(self, request, id, format=None):
        if request.user.user_type == 'SF':
            shop_catagory = self.get_shopCategory_object(id)
            serializer = ShopCategorySerializer(shop_catagory, data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self,request,id, format=None):
        if request.user.user_type == 'SF':
            shop_catagory = self.get_shopCategory_object(id)
            shop_catagory.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductCategoryDetails(APIView): # get product category id to get all the product meta list related to that product category id

    permission_classes = [GenericAuth]

    def get(self,request,id):
        obj = ProductCategory.objects.filter(id=id).first()
        if obj:
            productMetaList = obj.productmeta_set.all()
            serializer = ProductMetaSerializer(productMetaList,many=True)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)


class ProductMetaDetails(APIView):      # get product meta id to get all the product  list related to that product meta id

    permission_classes = [GenericAuth]

    def get(self,request,id):
        obj = ProductMeta.objects.filter(id=id).first()
        if obj:
            productList = obj.product_set.all()
            serializer = LatestProductSerializer(productList, many=True)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)


class RecentlyAddedProductList(APIView):  # return list of recently added products
    permission_classes = [GenericAuth]

    def get(self,request):
        queryset = Product.objects.all().order_by('-created_on')[:10]
        serializer = LatestProductSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




