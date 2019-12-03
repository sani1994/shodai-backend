import decimal

from django.shortcuts import render, get_object_or_404
from producer.serializers import ProducerFarmSerializer, ProducerBulkRequestSerializer, BusinessTypeSerializer, \
    ProducerBusinessSerializer, MicroBulkOrderProductsSerializer, \
    BulkOrderProductsSerializer, BulkOrderSerializer
from producer.models import ProducerBulkRequest, ProducerFarm, BusinessType, ProducerBusiness, MicroBulkOrderProducts, \
     BulkOrderProducts, BulkOrder

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

# Create your views here.
# from product.models import ProductUnit
# from product.serializers import ProductUnitSerializer
from sodai.utils.permission import GenericAuth


class PeroducerBulkRequestList(APIView):

    ## list of Producer
    permission_classes = [GenericAuth]

    def get(self, request, format=None):
        is_staff = request.user.is_staff
        queryset = ProducerBulkRequest.objects.all()
        if is_staff:
            queryset = ProducerBulkRequest.objects.all()
        else:
            user_type = request.user.user_type
            if user_type=='CM'or user_type== 'RT' :  # Customer = CM
                queryset = ProducerBulkRequest.objects.all(is_approved = True)
            elif user_type == 'PD':
                queryset = ProducerBulkRequest.objects.all(user = request.user)

            # elif user_type== 'PD': # Producer = PD
            #     producer = ProducerBulkRequest.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        serializer = ProducerBulkRequestSerializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = ProducerBulkRequestSerializer(data=request.data,context={'request':request})
        if request.user.user_type== 'SF':
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if request.user.user_type=='PD': # Producer = PD
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PeroducerBulkRequestDetails(APIView):
    """
    Retrieve, update and delete Producer
    """
    def get_producerProduct_object(self,id):
        obj = get_object_or_404(ProducerBulkRequest,id=id)
        return obj

    def get(self, request, id, format=None):
        obj = self.get_producerProduct_object( id)
        serializer = ProducerBulkRequestSerializer(obj)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        producer = self.get_producerProduct_object(id)
        serializer = ProducerBulkRequestSerializer(producer, data=request.data)
        if serializer.is_valid():
            if request.user.user_type=='SF':
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id, format=None):
        producer = self.get_producerProduct_object(id)
        if request.user.is_staff:
            producer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessTypeList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        queryset = BusinessType.objects.all()
        if queryset:
            serializer = BusinessTypeSerializer(queryset,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({
            "Status": "No content",
            "details": "Content not available"
        }, status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        if request.user.is_staff:
            serializer = BusinessTypeSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(created_by = request.user)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class BusinessTypeDetails(APIView):

    permission_classes = [GenericAuth]

    def get_businesstype_obj(self,id):
        obj = BusinessType.objects.get(id=id)
        return obj

    def get(self,request,id):
        obj = self.get_businesstype_obj(id)
        if obj:
            serializer = BusinessTypeSerializer(obj)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "Status": "No content",
            "details": "Content not available"
        }, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        if request.user.is_staff:
            obj = self.get_businesstype_obj(id)
            if obj:
                serializer = BusinessTypeSerializer(obj,data=request.data)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self,request,id):
        if request.user.is_staff:
            obj = self.get_businesstype_obj(id)
            if obj:
                obj.delete()
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProducerBusinessList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        if request.user.is_staff:
            queryset = ProducerBusiness.objects.all()
        elif request.user.user_type == 'PD':
            queryset= ProducerBusiness.objects.filter(user=request.user)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProducerBusinessSerializer(queryset,many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        if request.user.is_staff or request.user.user_type == 'PD':
            serializer = ProducerBusinessSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data,status= status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProducerBusinessDetails(APIView):

    permission_classes = [GenericAuth]

    def get_producerbusiness_obj(self,id):
        # obj = ProducerBusiness.objects.get(id=id)
        obj = get_object_or_404(ProducerBusiness,id=id)
        return obj

    def get(self,request,id):
        if request.user.is_staff or request.user.user_type=='PD':
            obj = self.get_producerbusiness_obj(id)
            serializer = ProducerBusinessSerializer(obj)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def put(self,request,id):
        if request.user.is_staff or request.user.user_type=='PD':
            obj = self.get_producerbusiness_obj(id)
            if obj:
                serializer = ProducerBusinessSerializer(obj,data=request.data)
                if serializer.is_valid():
                    serializer.save(modified_by = request.user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                    "Status": "No content",
                    "details": "Content not available"
                }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self,request,id):
        if request.user.is_staff or request.user.user_type=='PD':
            obj = self.get_producerbusiness_obj(id)
            if obj:
                obj.delete()
            return Response({
                    "Status": "No content",
                    "details": "Content not available"
                }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProducerFarmList(APIView):

    ## list of Producer Farm

    def get(self, request, format=None):
        is_staff = request.user.is_staff
        producer = ProducerFarm.objects.all()
        # if is_staff:
        #     producer_farm = ProducerFarm.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         producer_farm = ProducerFarm.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         producer = ProducerProduct.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         producer = ProducerProduct.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        serializer = ProducerFarmSerializer(producer, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProducerFarmSerializer(data=request.data)
        if request.user.user_type=='SF':
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if request.user.user_type=='PD': # Producer = PD
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProducerFarmDetail(APIView):
    """
    Retrieve, update and delete Producer
    """
    def get_producerFarm_object(self,id):
        obj = ProducerFarm.objects.filter(id=id).first()
        return obj

    def get(self, request, id, format=None):
        producerFarm = self.get_producerFarm_object(id)
        serializer = ProducerFarmSerializer(producerFarm)
        if serializer:
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        producerFarm= self.get_producerFarm_object(request, pk)
        serializer = ProducerFarmSerializer(producerFarm, data=request.data)
        if serializer.is_valid():
            if request.user.user_type=='SF':
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        producerFarm = self.get_producerFarm_object(request, pk)
        if request.user.is_staff:
            producerFarm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BulkOrderList(APIView):
    permission_classes = [GenericAuth]

    def get(self,request):
        quertset = BulkOrder.objects.all()
        serializer = BulkOrderSerializer(quertset,many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        serializer = BulkOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkOrderDetails(APIView):
    pass


# class CustomerMicroBulkOrderProductRequestList(APIView):
#
#     permission_classes = [GenericAuth]
#
#     def get(self,request):
#         if request.user.is_staff:
#             queryset = CustomerMicroBulkOrderProductRequest.objects.all()
#         elif request.user.user_type == 'CM':
#             queryset= CustomerMicroBulkOrderProductRequest.objects.filter(customer=request.user)
#         else:
#             return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
#         serializer = CustomerMicroBulkOrderProductRequestSerializer(queryset,many=True)
#         if serializer:
#             return Response(serializer.data,status=status.HTTP_200_OK)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#
#     def post(self,request):
#         if request.user.is_staff or request.user.user_type == 'CM':
#             obj = get_object_or_404(MicroBulkOrderProducts,id = request.data['micro_bulk_order_product'])
#             obj_qty = obj.qty
#             rqst_qty = self.request.data['qty']
#             diff = obj_qty-float(rqst_qty)
#             if diff< 0:
#                 return Response({'status: Product is out of stock.You can order :'+str(obj.qty)},status=status.HTTP_400_BAD_REQUEST)
#             serializer = CustomerMicroBulkOrderProductRequestSerializer(data=request.data,context={'request': request})
#             if serializer.is_valid():
#                 obj.qty=diff
#                 obj.save()
#                 serializer.save()
#                 return Response(serializer.data,status= status.HTTP_201_CREATED)
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#         return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
#
#
# class CustomerMicroBulkOrderProductRequestDetail(APIView):
#     """
#     Retrieve, update and delete Producer
#     """
#
#     def get_CustomerMicroBulkOrderProductRequest_object(self, id):
#         return get_object_or_404(CustomerMicroBulkOrderProductRequest, id=id)
#
#     def get(self, request, id, format=None):
#         obj = self.get_CustomerMicroBulkOrderProductRequest_object(id)
#         serializer = ProducerFarmSerializer(obj)
#         if serializer:
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def put(self, request, id, format=None):
#         obj = self.get_CustomerMicroBulkOrderProductRequest_object(id)
#         if MicroBulkOrderProducts.qty - request.data['qty'] < 0:
#             return Response({'status: Product is out of stock.You can order :' + str(MicroBulkOrderProducts.qty)},
#                             status=status.HTTP_400_BAD_REQUEST)
#         serializer = ProducerFarmSerializer(obj, data=request.data)
#         if serializer.is_valid():
#             if request.user.user_type == 'SF' or request.user.user_type == 'CM':
#                 serializer.save(modified_by=request.user)
#                 return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, id, format=None):
#         obj = self.get_CustomerMicroBulkOrderProductRequest_object(id)
#         if request.user.is_staff:
#             obj.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class ProducerProductListForCustomer(APIView):
    permission_classes = [GenericAuth]

    def get(self,request):
        if not request.user.user_type == 'PD':
            queryset = ProducerBulkRequest.objects.filter(is_approved = True)
            serializer = ProducerBulkRequestSerializer(queryset,many=True)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

