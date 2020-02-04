from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.shortcuts import render
from rest_framework.generics import get_object_or_404

from retailer.serializers import AccountSerializer, ShopSerializer, AcceptedOrderSerializer, \
    AcceptedOrderReadSerializer, ShopProductSerializer
from retailer.models import Account, Shop, AcceptedOrder, ShopProduct
from order.models import Order

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.db.models.functions import Distance
from datetime import datetime
# Create your views here.



# class RetailerList(APIView):
#
#     ## list of Retailer
#
#     def get(self, request, format=None):
#         is_staff = request.user.is_staff
#         retailer = Retailer.objects.all()
#         # if is_staff:
#         #     product = Product.objects.all()
#         # else:
#         #     user_type = request.user.user_type
#         #     if user_type=='CM':  # Customer = CM
#         #         product = Product.objects.filter(created_by=request.user)
#         #     elif user_type=='RT': # Retailer = RT
#         #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#
#
#         #     elif user_type== 'PD': # Producer = PD
#         #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#             # elif user_type== 'SF': # Staff = SF
#             #     order = Order.objects.filter(created_by=request.user)
#
#         serializer = RetailerSerializer(retailer, context={'request': request})
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = RetailerSerializer(data=request.data)
#         if request.user.is_staff:
#             if serializer.is_valid():
#                 serializer.save(created_by=request.user)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         else:
#             if request.user.user_type=='RT': # Retailer = RT
#                 if serializer.is_valid():
#                     serializer.save(created_by=request.user)
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#
#
# class RetailerDetail(APIView):
#     """
#     Retrieve, update and delete Orders
#     """
#     def get_object(self, request, pk):
#         is_staff = request.user.is_staff
#         try:
#             if is_staff:
#                 return Retailer.objects.get(pk=pk)
#             else:
#                 user_type = request.user.user_type
#                 if user_type=='CM':  # Customer = CM
#                     return Retailer.objects.get(pk=pk)
#                 elif user_type=='RT': # Retailer = RT
#                     return Retailer.objects.get(pk=pk)
#                     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#                 elif user_type== 'PD': # Producer = PD
#                     return Retailer.objects.get(pk=pk)
#                      # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#                 return Retailer.objects.get(pk=pk)
#         except Retailer.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         retailer = self.get_object(request, pk)
#         serializer = RetailerSerializer(retailer, data=request.data)
#         if serializer.is_valid():
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#     def put(self, request, pk, format=None):
#         retailer = self.get_object(request, pk)
#         serializer = RetailerSerializer(retailer, data=request.data)
#         if serializer.is_valid():
#             if request.user==Retailer.created_by or request.user.is_staff:
#                 serializer.save(modified_by=request.user)
#                 return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         retailer = self.get_object(request, pk)
#         if request.user.is_staff:
#             retailer.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
from sodai.utils.permission import GenericAuth


# class AccountList(APIView):
#
#     permission_classes = [GenericAuth]
#
#     ## list of Retailer' Account
#
#     def get(self, request, format=None):
#         is_staff = request.user.is_staff
#         account = Account.objects.all()
#         # if is_staff:
#         #     account = Account.objects.all()
#         # else:
#         #     user_type = request.user.user_type
#         #     if user_type=='CM':  # Customer = CM
#         #         account = Account.objects.filter(created_by=request.user)
#         #     elif user_type=='RT': # Retailer = RT
#         #         aroduct = Account.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#
#
#         #     elif user_type== 'PD': # Producer = PD
#         #         account = Account.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#             # elif user_type== 'SF': # Staff = SF
#             #     order = Order.objects.filter(created_by=request.user)
#
#         serializer = AccountSerializer(account, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = AccountSerializer(data=request.data,context={'request': request})
#         if request.user.is_staff:
#             if serializer.is_valid():
#                 serializer.save(created_by=request.user)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         else:
#             if request.user.user_type=='RT': # Retailer = RT
#                 if serializer.is_valid():
#                     serializer.save(created_by=request.user)
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#
#
# class AccountDetail(APIView):
#     """
#     Retrieve, update and delete Orders
#     """
#     def get_object(self, request, id):
#         is_staff = request.user.is_staff
#         try:
#             if is_staff:
#                 return Account.objects.get(pk=pk)
#             else:
#                 user_type = request.user.user_type
#                 if user_type=='CM':  # Customer = CM
#                     return Account.objects.get(pk=pk)
#                 elif user_type=='RT': # Retailer = RT
#                     return Account.objects.get(pk=pk)
#                     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#                 elif user_type== 'PD': # Producer = PD
#                     return Account.objects.get(pk=pk)
#                      # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#                 return Account.objects.get(pk=pk)
#         except Account.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         account = self.get_object(request, pk)
#         serializer = AccountSerializer(account, data=request.data)
#         if serializer.is_valid():
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#     def put(self, request, pk, format=None):
#         account = self.get_object(request, pk)
#         serializer = AccountSerializer(account, data=request.data)
#         if serializer.is_valid():
#             if request.user==Account.created_by or request.user.is_staff:
#                 serializer.save(modified_by=request.user)
#                 return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         account= self.get_object(request, pk)
#         if request.user.is_staff:
#             account.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
from userProfile.models import UserProfile


class ShopList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        if request.user.user_type == 'RT':
            user_id = request.user.id
            obj = Shop.objects.filter(user_id=user_id,is_approved=True)
            if obj:
                serializer = ShopSerializer(obj,many=True)
                if serializer:
                    return Response(serializer.data,status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        # elif request.user.user_type == 'CM':
        #     return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
        else:
            obj = Shop.objects.all()
            if obj:
                serializer = ShopSerializer(obj,many=True)
                if serializer:
                    return Response(serializer.data,status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        if request.user.user_type == 'RT':
            serializer = ShopSerializer(data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ShopDetail(APIView):

    permission_classes = [GenericAuth]

    def get_shop_object(self,id):
        obj = Shop.objects.filter(id = id).first()
        return obj

    def get(self,request,id):
        if request.user.user_type == 'RT':
            obj = self.get_shop_object(id)
            if obj:
                serializer = ShopSerializer(obj)
                if serializer:
                    return Response(serializer.data,status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def put(self,request,id):
        if request.user.user_type=='RT':
            obj = self.get_shop_object(id)
            if obj.user_id == request.user.id:  # if user only the owner of the fetched object make make this operation
                if obj:
                    serializer = ShopSerializer(obj,data=request.data,context={'request':request})
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data,status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self,request,id):
        if request.user.user_type=='RT':
            obj = self.get_shop_object(id)
            if obj:
                if obj.user_id == request.user.id:
                    obj.delete()
                    return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class AccountList(APIView):
    permission_classes = [GenericAuth]

    def get(self,request):
        if request.user.user_type=='RT':
            user_id = request.user.id
            obj = Account.objects.filter(user_id=user_id)
            if obj:
                serializer = AccountSerializer(obj,many=True)
                if serializer:
                    return Response(serializer.data,status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type == 'SF':
            obj = Account.objects.all()
            if obj:
                serializer = AccountSerializer(obj,many=True)
                if serializer:
                    return Response(serializer.data,status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def post(self,request):
        if request.user.user_type=='RT':
            serializer = AccountSerializer(data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save(created_by = request.user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class AccountDetail(APIView):

    permission_classes = [GenericAuth]

    def get_account_obj(self,id):
        obj = Account.objects.filter(id = id).first()
        return obj

    def get(self,request,id):
        if request.user.user_type=='RT':
            user_id = request.user.id
            obj = self.get_account_obj(id)
            if obj:
                if obj.user_id==user_id:
                    serializer = AccountSerializer(obj)
                    if serializer:
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def put(self,request,id):
        if request.user.user_type=='RT':
            user_id = request.user.id
            obj = self.get_account_obj(id)
            if obj:
                if obj.user_id==user_id:
                    serializer = AccountSerializer(obj,data=request.data,context={'request': request})
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self,request,id):
        if request.user.user_type=='RT':
            user_id = request.user.id
            obj = self.get_account_obj(id)
            if obj:
                if obj.user_id==user_id:
                    obj.delete()
                    return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class AcceptedOrderList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        if request.user.user_type == 'RT':
            user = request.user
            obj = AcceptedOrder.objects.filter(user_id= user)
            if obj:
                serializer = AcceptedOrderReadSerializer(obj,many=True)
                if serializer:
                    return Response(serializer.data,status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = []            # front end cannot hendle single object
                response.append(
                    {
                        "id": 0,
                        "created_on": "2020-02-04T12:15:51.995451+06:00",
                        "modified_on": "2020-02-04T12:15:51.995748+06:00",
                        "created_by": " ",
                        "modified_by": " ",
                        "user": {
                            "id": 28,
                            "password": "pbkdf2_sha256$150000$o9jeeoDOMQHk$tGreovlksbG47PqggCrTi+aBP1/HPm2cZpatfj8c0fM=",
                            "last_login": " ",
                            "is_superuser": False,
                            "username": "+88000000000000",
                            "is_staff": False,
                            "is_active": True,
                            "date_joined": "2020-01-30T14:42:02+06:00",
                            "user_type": "RT",
                            "user_image": " ",
                            "mobile_number": "+88000000000000",
                            "first_name": "sajib",
                            "last_name": "sajib",
                            "email": "nishat@nishat.com",
                            "user_NID": "142739047262729",
                            "ref_code": " ",
                            "pin_code": " ",
                            "created_on": "2020-01-30T14:42:02+06:00",
                            "modified_on": " ",
                            "is_approved": True,
                            "groups": [],
                            "user_permissions": []
                        },
                        "shop": " ",
                        "order": {
                            "id": 74,
                            "created_on": "2020-02-04T11:57:00.208849+06:00",
                            "modified_on": "2020-02-04T12:15:51.989411+06:00",
                            "delivery_date_time": "2020-02-04T12:15:51.989420+06:00",
                            "delivery_place": "Banani",
                            "order_total_price": 60.0,
                            "lat": 23.7937,
                            "long": 90.4066,
                            "order_geopoint": " ",
                            "order_status": "OA",
                            "home_delivery": True,
                            "order_type": "FP",
                            "contact_number": "+8801747162600",
                            "created_by": 2,
                            "modified_by": " ",
                            "user": 2,
                            "address": " "
                        },
                        "order_product": " "
                    }
                )
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type =='SF':
            obj = AcceptedOrder.objects.all()
            serializer = AcceptedOrderReadSerializer(obj,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request):
        if request.user.user_type == 'RT':
            order = request.data['order']
            serializer = AcceptedOrderSerializer(data=request.data,context={'request':request})
            if serializer.is_valid():
                order_obj = Order.objects.get(id = order)
                setattr(order_obj,'order_status','OA')
                order_obj.save()
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class AcceptedOrderDetail(APIView):

    permission_classes = [GenericAuth]

    def get_accepted_order_obj(self,id):
        obj = AcceptedOrder.objects.filter(id = id).first()
        return obj

    def get(self,request,id):
        obj = self.get_accepted_order_obj(id)
        serializer = AcceptedOrderReadSerializer(obj)
        if serializer:
            return  Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        obj = AcceptedOrder.objects.filter(id=id).first
        if obj.user_id == request.user.id:
            obj.delete()
            return Response({'status': "Delete Successfull..!!"},status=status.HTTP_200_OK)
        return Response({'status': 'Request Unseccessful..!!'},status=status.HTTP_400_BAD_REQUEST)


class RetailerShopList(APIView):

    permission_classes = [GenericAuth]

    # def get_user_obj(self,id):
    #     obj = UserProfile.objects.get(id=id)
    #     return obj

    def get(self,request,id):
        if request.user.user_type == 'RT':
            shop = get_object_or_404(Shop,user=request.user)
            if shop:
                serializer = ShopSerializer(shop)
                if serializer:
                    return Response(serializer.data,status=status.HTTP_200_OK)
                # return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ShopProductList(APIView):
    permission_classes = [GenericAuth]

    def get(self,request):
        if request.user.user_type == 'RT':
            shop = Shop.objects.get(user=request.user)
            product_list = ShopProduct.objects.filter(shop=shop)
            serializer = ShopProductSerializer(product_list,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def post(self,request):
        if request.user.user_type == 'RT':
            serializer = ShopProductSerializer(data= request.data,context={'request':request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ShopPeroductDetail(APIView):
    permission_classes = [GenericAuth]

    def get(self,request,id):
        product = get_object_or_404(ShopProduct,id=id)
        serializer = ShopProductSerializer(product)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self,request,id):
        product = get_object_or_404(ShopProduct, id=id)
        serializer = ShopProductSerializer(product,data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)

    def delete(self,request,id):
        product = get_object_or_404(ShopProduct, id=id)
        product.delete()
        return Response({'Delete Successful'}, status=status.HTTP_200_OK)


class HasShop(APIView):
    permission_classes = [GenericAuth]

    def get(self,request):
        has_shop = Shop.objects.filter(user=request.user)
        if has_shop:
            if not has_shop.is_approved:
                return Response("waiting for admin approval for your shop",status=status.HTTP_401_UNAUTHORIZED)
            return Response({"True"},status=status.HTTP_200_OK)
        return Response({"False"},status=status.HTTP_204_NO_CONTENT)


class ShopProductForCustomer(APIView):
    permission_classes = [GenericAuth]

    def get(self,request):
        user_location = GEOSGeometry('POINT(%f %f)' % (float(request.data['long']),float(request.data['lat'])))
        near_by_shop_list = Shop.objects.filter(shop_geopoint__distance_lte=(user_location, D(m=100))).annotate(distance=Distance('shop_geopoint', user_location)).order_by('distance')
        if not near_by_shop_list:
            return Response("No nearby shops are there.",status=status.HTTP_204_NO_CONTENT)
        products = []
        for shop in near_by_shop_list:
            product = shop.shopproduct_set.all().distinct('product__id')
            serializer = ShopProductSerializer(product,many=True)
            for data in serializer.data:
                products.append(data)
        if not products:
            return Response("No available products in shop.", status=status.HTTP_204_NO_CONTENT)
        return Response(products,status=status.HTTP_200_OK)


class GetNearbyShops(APIView):
    permission_classes = [GenericAuth]

    def get(self,request):
        user_location = GEOSGeometry('POINT(%f %f)' % (float(request.data['long']),float(request.data['lat'])))
        near_by_shop_list = Shop.objects.filter(shop_geopoint__distance_lte=(user_location, D(m=100))).annotate(distance=Distance('shop_geopoint', user_location)).order_by('distance')
        if not near_by_shop_list:
            return Response("No nearby shops are there.",status=status.HTTP_204_NO_CONTENT)
        serializer = ShopSerializer(near_by_shop_list,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class GetNearbyShopProducts(APIView):
    permission_classes = [GenericAuth]

    def get(self,request,id): # id = shop_id
        shop = Shop.objects.get(id = id)
        products = shop.shopproduct_set.all()
        serializer = ShopProductSerializer(products,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


