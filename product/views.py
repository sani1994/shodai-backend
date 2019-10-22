from django.shortcuts import render
from rest_framework.generics import get_object_or_404

import product
from product.serializers import ShopCategorySerializer, ProductCategorySerializer, ProductSerializer, ProductMetaSerializer
from product.models import ShopCategory, ProductMeta, ProductCategory, Product

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

    permission_classes = [GenericAuth]

    ## list of Prodect


    def get(self, request, format=None):
        # is_staff = request.user.is_staff
        product = Product.objects.all()
        # if is_staff:
        #     product = Product.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         product = Product.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        # if request.user.is_staff:
        #     if serializer.is_valid():
        #         serializer.save(created_by=request.user)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        #
        # else:
        #     if request.user.user_type=='RT': # Retailer = RT
        #         if serializer.is_valid():
        #             serializer.save(created_by=request.user)
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data,status.HTTP_202_ACCEPTED)
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProductDetail(APIView):
    """
    Retrieve, update and delete Orders
    """

    permission_classes = [GenericAuth]

    def get_object(self, request, id):
        # is_staff = request.user.is_staff
        # try:
        #     if is_staff:
        #         return Product.objects.get(pk=pk)
        #     else:
        #         user_type = request.user.user_type
        #         if user_type=='CM':  # Customer = CM
        #             return Product.objects.get(pk=pk)
        #         elif user_type=='RT': # Retailer = RT
        #             return Product.objects.get(pk=pk)
        #             # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         elif user_type== 'PD': # Producer = PD
        #             return Product.objects.get(pk=pk)
        #              # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         return Product.objects.get(pk=pk)
        try:
            return Product.objects.filter(id=id).first()
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):

        product = self.get_object(request, id)
        if product:
            serializer = ProductSerializer(product)
            if serializer:
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Rontent not available"
                },status=status.HTTP_204_NO_CONTENT)
    

    def put(self, request, id, format=None):
        product = self.get_object(request, id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            # if request.user==product.created_by or request.user.is_staff:
            #     serializer.save(modified_by=request.user)
            #     return Response(serializer.data)
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id, format=None):
        product = self.get_object(request,id)
        # if request.user==product.created_by or request.user.is_staff:
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProductMetaList(APIView):

    ## list of Prodect Meta (original product name with comapny name)
    permission_classes = [GenericAuth]

    def get(self, request, format=None):
        # is_staff = request.user.is_staff
        product_meta = ProductMeta.objects.filter()
        # if is_staff:
        #     product = Product.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         product = Product.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        serializer = ProductMetaSerializer(product_meta, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductMetaSerializer(data=request.data,context={'request':request})
        # if request.user.is_staff:
        #     if serializer.is_valid():
        #         serializer.save(created_by=request.user)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        #
        # else:
        #     if request.user.user_type=='RT': # Retailer = RT
        #         if serializer.is_valid():
        #             serializer.save(created_by=request.user)
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProductMetaDetail(APIView):     # this mathod dont work because couldnt update and retriev object of productMea object
    """
    Retrieve, update and delete Orders
    """
    permission_classes = [GenericAuth]
    def get_object(self,request, id):
        # is_staff = request.user.is_staff
        # try:
        #     if is_staff:
        #         return ProductMeta.objects.get(pk=pk)
        #     else:
        #         user_type = request.user.user_type
        #         if user_type=='CM':  # Customer = CM
        #             return ProductMeta.objects.get(pk=pk)
        #         elif user_type=='RT': # Retailer = RT
        #             return ProductMeta.objects.get(pk=pk)
        #             # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         elif user_type== 'PD': # Producer = PD
        #             return ProductMeta.objects.get(pk=pk)
        #              # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         return ProductMeta.objects.get(pk=pk)
        try:
            obj= ProductMeta.objects.filter(id=id).first()
            return obj
        except ProductMeta.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        # print(pk)
        product_meta = self.get_object(request,id)
        if product_meta:
            serializer = ProductMetaSerializer(product_meta)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Rontent not available"
                },status=status.HTTP_204_NO_CONTENT)
    

    def put(self, request, id, format=None):
        product_meta = self.get_object(request,id)
        serializer = ProductMetaSerializer(product_meta, data=request.data)
        if serializer.is_valid():
            # if request.user==product_meta.created_by or request.user.is_staff:
            #     serializer.save(modified_by=request.user)
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id, format=None):
        product_meta = self.get_object(request,id)
        # if request.user.is_staff:
        product_meta.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ProductCategoryList(APIView):
    query = ProductCategory.objects.all()
    ## list of Prodect category

    def get(self, request, format=None):
        # is_staff = request.user.is_staff
        product_catagory = ProductCategory.objects.all()
        # if is_staff:
        #     product = Product.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         product = Product.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        # serializer = ProductCategorySerializer(product_catagory, many=True, context={'request': request}) // ago
        serializer = ProductCategorySerializer(product_catagory, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductCategorySerializer(data=request.data,context={'request': request})
        # if request.user.is_staff:
        #     if serializer.is_valid():
        #         serializer.save(created_by=request.user)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        #
        # else:
        #     if request.user.user_type=='RT': # Retailer = RT
        #         if serializer.is_valid():
        #             serializer.save(created_by=request.user)
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)

        if serializer:
            if serializer.is_valid():
                serializer.save()
                # serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductCategoryDetail(APIView):
    permission_classes = [GenericAuth]

    # """
    # Retrieve, update and delete Orders
    # """
    def get_object(self,request,id):     # enable another peremeter "request" when to access user
        try:
            object = ProductCategory.objects.filter(id=id).first()
            return object
        except ProductCategory.DoesNotExist:
            raise Http404

        # is_staff = request.user.is_staff
        # try:
        #     if is_staff:
        #         return ProductCategory.objects.get(pk=pk)
        #     else:
        #         user_type = request.user.user_type
        #         if user_type=='CM':  # Customer = CM
        #             return ProductCategory.objects.get(pk=pk)
        #         elif user_type=='RT': # Retailer = RT
        #             return ProductCategory.objects.get(pk=pk)
        #             # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         elif user_type== 'PD': # Producer = PD
        #             return ProductCategory.objects.get(pk=pk)
        #              # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         return ProductCategory.objects.get(pk=pk)
        # except ProductCategory.DoesNotExist:
        #     raise Http404

    def get(self, request, id,format=None):
        product_catagory = self.get_object(request,id)
        if product_catagory:
            serializer = ProductCategorySerializer(product_catagory)
            if serializer:
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id, format=None):
        product_catagory = self.get_object(request,id)
        serializer = ProductCategorySerializer(product_catagory, data=request.data)
        if serializer.is_valid():
            # if request.user==product_catagory.created_by or request.user.is_staff: enable when user will be avilable
            #     serializer.save(modified_by=request.user)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request, id, format=None):
        product_catagory = self.get_object(request,id)
        print(product_catagory)
        # if request.user.is_staff:
        #     ProductCategory.delete()
        product_catagory.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopCategoryList(APIView):        # shop_category must be in unique formate to make the connection with shop model of retailer
    permission_classes = [GenericAuth]

    ## list of Shop category

    def get(self, request, format=None):
        # is_staff = request.user.is_staff
        shop_catagory = ShopCategory.objects.all()
        # if is_staff:
        #     product = Product.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         product = Product.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        serializer = ShopCategorySerializer(shop_catagory, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ShopCategorySerializer(data=request.data)
        # if request.user.is_staff:
        #     if serializer.is_valid():
        #         serializer.save(created_by=request.user)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

        # else:
        #     if request.user.user_type=='RT': # Retailer = RT
        #         if serializer.is_valid():
        #             serializer.save(created_by=request.user)
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ShopCategoryDetail(APIView):

    permission_classes = [GenericAuth]
    """
    Retrieve, update and delete Orders
    """
    def get_object(self,request,id):
        # is_staff = request.user.is_staff
        try:
            # if is_staff:
            #     return ShopCategory.objects.get(pk=pk)
            # else:
            #     user_type = request.user.user_type
            #     if user_type=='CM':  # Customer = CM
            #         return ShopCategory.objects.get(pk=pk)
            #     elif user_type=='RT': # Retailer = RT
            #         return ShopCategory.objects.get(pk=pk)
            #         # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            #     elif user_type== 'PD': # Producer = PD
            #         return ShopCategory.objects.get(pk=pk)
            #          # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            #     return ShopCategory.objects.get(pk=pk)
            object = ShopCategory.objects.filter(id=id).first
            return object
        except ShopCategory.DoesNotExist:
            raise Http404

    def get(self,request,id, format=None):
        shop_catagory = self.get_object(request,id)
        if shop_catagory:
            serializer = ShopCategorySerializer(shop_catagory)
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
        shop_catagory = self.get_object( request,id)
        serializer = ShopCategorySerializer(shop_catagory, data=request.data)
        if serializer.is_valid():
            # if request.user==shop_catagory.created_by or request.user.is_staff:
            #     serializer.save(modified_by=request.user)
            #     return Response(serializer.data)
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id, format=None):
        shop_catagory = self.get_object(request,id)
        # if request.user==ProductCategory.created_by or request.user.is_staff:
        #     Product.delete()
        shop_catagory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductCategoryDetails(APIView): # post product category id to get all the product meta list related to that product category id

    permission_classes = [GenericAuth]

    def post(self,request,id):
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


class ProductMetaDetails(APIView):      # post product meta id to get all the product  list related to that product meta id

    permission_classes = [GenericAuth]

    def post(self,request,id):
        obj = ProductMeta.objects.filter(id=id).first()
        if obj:
            productList = obj.product_set.all()
            serializer = ProductSerializer(productList,many=True)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)



