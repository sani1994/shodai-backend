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

class ProductList(APIView):
    # permission_classes = (IsAuthenticated,)

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
            
        serializer = ProductSerializer(product, many=True, context={'request': request})
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
            serializer.save()
            return Response(status.HTTP_202_ACCEPTED)
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProductDetail(APIView):
    """
    Retrieve, update and delete Orders
    """
    def get_object(self, request, pk):
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
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(request, pk)
        print(product)
        serializer = ProductSerializer(product,data=product)
        print(serializer)
        if serializer.is_valid():
            print((serializer.data))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        product = self.get_object(request, pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            # if request.user==product.created_by or request.user.is_staff:
            #     serializer.save(modified_by=request.user)
            #     return Response(serializer.data)
            serializer.save()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        product = self.get_object(request, pk)
        if request.user==product.created_by or request.user.is_staff:
            product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProductMetaList(APIView):

    ## list of Prodect Meta (original product name with comapny name)

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
            
        serializer = ProductMetaSerializer(product_meta, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductMetaSerializer(data=request.data)
        print("input serializer: ",serializer)
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
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProductMetaDetail(APIView):     # this mathod dont work because couldnt update and retriev object of productMea object
    """
    Retrieve, update and delete Orders
    """
    def get_object(self, pk):
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
            objectt= ProductMeta.objects.get(pk=pk)
            return objectt
        except ProductMeta.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        # print(pk)
        product_meta = self.get_object(pk)
        serializer = ProductMetaSerializer(data=product_meta)
        if serializer.is_valid():
            print(serializer.data)
            return Response(serializer.data)
        return Response({" 'Status_code': 400  "}, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        product_meta = self.get_object(pk)
        print(product_meta.data)
        serializer = ProductMetaSerializer(product_meta, data=request.data)
        print(serializer)
        if serializer.is_valid():
            # if request.user==product_meta.created_by or request.user.is_staff:
            #     serializer.save(modified_by=request.user)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        product_meta = self.get_object(pk)
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
        serializer = ProductCategorySerializer(data=request.data)
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
                # serializer.save(created_by=request.user)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductCategoryDetail(APIView):
    """
    Retrieve, update and delete Orders
    """
    def get_object(self,pk):     # enable another peremeter "request" when to access user
        try:
            object = ProductCategory.objects.get(pk=pk)
            print(object)
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

    def get(self, request, pk,format=None):
        product_catagory = self.get_object(pk)
        serializer = ProductCategorySerializer(data=product_catagory)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        product_catagory = self.get_object(pk)
        serializer = ProductCategorySerializer(product_catagory, data=request.data)
        if serializer.is_valid():
            # if request.user==product_catagory.created_by or request.user.is_staff: enable when user will be avilable
            #     serializer.save(modified_by=request.user)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request, pk, format=None):
        product_catagory = self.get_object(pk)
        print(product_catagory)
        # if request.user.is_staff:
        #     ProductCategory.delete()
        product_catagory.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopCategoryList(APIView):

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
            
        serializer = ShopCategorySerializer(shop_catagory, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        print(request)
        serializer = ShopCategorySerializer(data=request.data)
        # if request.user.is_staff:
        #     if serializer.is_valid():
        #         serializer.save(created_by=request.user)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        if serializer.is_valid():
            serializer.save()
            return Response({'success':'success'},status=status.HTTP_202_ACCEPTED)

        # else:
        #     if request.user.user_type=='RT': # Retailer = RT
        #         if serializer.is_valid():
        #             serializer.save(created_by=request.user)
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ShopCategoryDetail(APIView):
    """
    Retrieve, update and delete Orders
    """
    def get_object(self, pk):
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
            object = ShopCategory.objects.get(pk=pk)
            print(object)
            return object
        except ShopCategory.DoesNotExist:
            raise Http404

    def get(self,request,pk, format=None):
        shop_catagory = self.get_object(pk)
        print(shop_catagory)
        serializer = ShopCategorySerializer(shop_catagory,data = shop_catagory)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        shop_catagory = self.get_object( pk)
        serializer = ShopCategorySerializer(shop_catagory, data=request.data)
        if serializer.is_valid():
            # if request.user==shop_catagory.created_by or request.user.is_staff:
            #     serializer.save(modified_by=request.user)
            #     return Response(serializer.data)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk, format=None):
        shop_catagory = self.get_object( pk)
        # if request.user==ProductCategory.created_by or request.user.is_staff:
        #     Product.delete()
        shop_catagory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        