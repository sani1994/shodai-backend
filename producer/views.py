import decimal

from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from producer.serializers import ProducerFarmSerializer, ProducerBulkRequestSerializer, BusinessTypeSerializer, \
    ProducerBusinessSerializer, MicroBulkOrderProductsSerializer, \
    BulkOrderProductsSerializer, BulkOrderSerializer, BulkOrderProductsReadSerializer, MicroBulkOrderSerializer
from producer.models import ProducerBulkRequest, ProducerFarm, BusinessType, ProducerBusiness, MicroBulkOrderProducts, \
    BulkOrderProducts, BulkOrder, MicroBulkOrder
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

# Create your views here.
# from product.models import ProductUnit
# from product.serializers import ProductUnitSerializer
from sodai.utils.permission import GenericAuth


class PeroducerBulkRequestList(APIView):  # get producer bulk request(producer's product request to sell) list and create

    ## list of Producer
    permission_classes = [GenericAuth]

    def get(self, request, format=None):
            user_type = request.user.user_type
            if user_type == 'CM' or user_type == 'RT':  # Customer = CM
                queryset = ProducerBulkRequest.objects.filter(is_approved=True)
                serializer = ProducerBulkRequestSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif user_type == 'PD':
                queryset = ProducerBulkRequest.objects.filter(user=request.user)
                serializer = ProducerBulkRequestSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = ProducerBulkRequestSerializer(data=request.data, context={'request': request})
        # if request.user.user_type == 'SF':
        #     if serializer.is_valid():
        #         serializer.save()
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        # if request.user.user_type == 'PD':  # Producer = PD
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)


class PeroducerBulkRequestDetails(APIView):  # get producer bulk request(producer's product request to sell) ,update delete
    """
    Retrieve, update and delete Producer
    """
    def get_producerProduct_object(self, id):
        obj = get_object_or_404(ProducerBulkRequest, id=id)
        return obj

    def get(self, request, id, format=None):
        obj = self.get_producerProduct_object(id)
        serializer = ProducerBulkRequestSerializer(obj)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        producer = self.get_producerProduct_object(id)
        serializer = ProducerBulkRequestSerializer(producer, data=request.data)
        if serializer.is_valid():
            if request.user.user_type == 'SF':
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        producer = self.get_producerProduct_object(id)
        if request.user.is_staff:
            producer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessTypeList(APIView):  # get business type list and create

    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = BusinessType.objects.all()
        if queryset:
            serializer = BusinessTypeSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({
            "Status": "No content",
            "details": "Content not available"
        }, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        if request.user.is_staff:
            serializer = BusinessTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class BusinessTypeDetails(APIView):  # business type get, update and delete

    permission_classes = [GenericAuth]

    def get_businesstype_obj(self, id):
        obj = BusinessType.objects.get(id=id)
        return obj

    def get(self, request, id):
        obj = self.get_businesstype_obj(id)
        if obj:
            serializer = BusinessTypeSerializer(obj)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "Status": "No content",
            "details": "Content not available"
        }, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id):
        if request.user.is_staff:
            obj = self.get_businesstype_obj(id)
            if obj:
                serializer = BusinessTypeSerializer(obj, data=request.data)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        if request.user.is_staff:
            obj = self.get_businesstype_obj(id)
            if obj:
                obj.delete()
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProducerBusinessList(APIView):  # get producer business list and create

    permission_classes = [GenericAuth]

    def get(self, request):
        if request.user.is_staff:
            queryset = ProducerBusiness.objects.all()
        elif request.user.user_type == 'PD':
            queryset = ProducerBusiness.objects.filter(user=request.user)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProducerBusinessSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.user.is_staff or request.user.user_type == 'PD':
            serializer = ProducerBusinessSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProducerBusinessDetails(APIView):  # producer business get ,update and delete

    permission_classes = [GenericAuth]

    def get_producerbusiness_obj(self, id):
        # obj = ProducerBusiness.objects.get(id=id)
        obj = get_object_or_404(ProducerBusiness, id=id)
        return obj

    def get(self, request, id):
        if request.user.is_staff or request.user.user_type == 'PD':
            obj = self.get_producerbusiness_obj(id)
            serializer = ProducerBusinessSerializer(obj)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, id):
        if request.user.is_staff or request.user.user_type == 'PD':
            obj = self.get_producerbusiness_obj(id)
            if obj:
                serializer = ProducerBusinessSerializer(obj, data=request.data)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        if request.user.is_staff or request.user.user_type == 'PD':
            obj = self.get_producerbusiness_obj(id)
            if obj:
                obj.delete()
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProducerFarmList(APIView):  # get producer farm and create

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
        if request.user.user_type == 'SF':
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if request.user.user_type == 'PD':  # Producer = PD
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProducerFarmDetail(APIView):  # producer farm get,update and delete
    """
    Retrieve, update and delete Producer
    """

    def get_producerFarm_object(self, id):
        obj = ProducerFarm.objects.filter(id=id).first()
        return obj

    def get(self, request, id, format=None):
        producerFarm = self.get_producerFarm_object(id)
        serializer = ProducerFarmSerializer(producerFarm)
        if serializer:
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        producerFarm = self.get_producerFarm_object(request, id)
        serializer = ProducerFarmSerializer(producerFarm, data=request.data)
        if serializer.is_valid():
            if request.user.user_type == 'SF':
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        producerFarm = self.get_producerFarm_object(request, id)
        if request.user.is_staff:
            producerFarm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BulkOrderList(APIView):
    """
    get list of bulk order
    """

    permission_classes = [GenericAuth]

    def get(self, request):
        quertset = BulkOrder.objects.all()
        serializer = BulkOrderSerializer(quertset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = BulkOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkOrderDetails(APIView):
    """
    Retrieve, update and delete Producer
    """
    permission_classes = [GenericAuth]

    def get_bulkorderdetail_object(self, id):
        return get_object_or_404(BulkOrder, id=id)

    def get(self, request, id, format=None):
        queryset = self.get_bulkorderdetail_object(id)
        serializer = BulkOrderSerializer(queryset)
        if serializer:
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        queryset = self.get_bulkorderdetail_object(id)
        serializer = BulkOrderSerializer(queryset, data=request.data)
        if serializer.is_valid():
            if request.user.user_type == 'SF':
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        obj = self.get_bulkorderdetail_object(id)
        if request.user.is_staff:
            obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BulkOrderProductsList(APIView):
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = BulkOrderProducts.objects.all()
        serializer = BulkOrderProductsReadSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.user.is_staff:
            serializer = BulkOrderProductsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkOrderProductsDetails(APIView):
    permission_classes = [GenericAuth]

    def get_bulkorderproducts_obj(self, id):
        return get_object_or_404(BulkOrderProducts, id=id)

    def get(self, request, id):
        queryobj = self.get_bulkorderproducts_obj(id)
        serializer = BulkOrderProductsReadSerializer(queryobj)
        if serializer:
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        queryobj = self.get_bulkorderproducts_obj(id)
        serializer = BulkOrderProductsSerializer(queryobj, data=request.data)
        if serializer.is_valid():
            if request.user.user_type == 'SF':
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        obj = self.get_bulkorderproducts_obj(id)
        if request.user.is_staff:
            obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

class ProducerProductListForCustomer(APIView):  # get bulk order products list from start date to expired date
    permission_classes = [GenericAuth]

    def get(self, request):
        if not request.user.user_type == 'PD':
            current_time = timezone.now()
            bulk_order_product = []
            queryset = BulkOrderProducts.objects.all()
            for obj in queryset:
                if obj.bulk_order.start_date <= current_time <= obj.bulk_order.expire_date:
                    bulk_order_product.append(obj)
            if not bulk_order_product:
                return Response({'status: No Data Available'}, status=status.HTTP_204_NO_CONTENT)
            serializer = BulkOrderProductsReadSerializer(bulk_order_product, many=True)
            if serializer:
                objects = serializer.data
                for object in objects:
                    object['product_name'] = object['product']['product_name']
                    object['product_image'] = object['product']['product_image']
                    object['bulk_order_id'] = object['bulk_order']['id']
                    object['bulk_order_product_id'] = object['id']
                    object['bulk_order_product_unit'] = object['unit']['product_unit']
                    object.pop("product")
                    object.pop('bulk_order')
                    object.pop('unit')
                return Response(objects, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MicroBulkOrderList(APIView):
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = []
        if request.user.user_type == 'SF':
            queryset = MicroBulkOrder.objects.all()
        elif request.user.user_type == 'CM':
            queryset = MicroBulkOrder.objects.filter(customer=request.user)
        serializer = MicroBulkOrderSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = MicroBulkOrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MicroBulkOrderDetails(APIView):
    permission_classes = [GenericAuth]

    def get_microbulkorder_obj(self, id):
        return get_object_or_404(MicroBulkOrder, id=id)

    def get(self, request, id):
        queryobj = self.get_microbulkorder_obj(id)
        serializer = MicroBulkOrderSerializer(queryobj)
        if serializer:
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        queryobj = self.get_microbulkorder_obj(id)
        serializer = MicroBulkOrderSerializer(queryobj, data=request.data)
        if serializer.is_valid():
            if request.user.user_type == 'SF':
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        obj = self.get_microbulkorder_obj(id)
        if request.user.is_staff:
            obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MicroBulkOrderProductsList(APIView):
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = []
        if request.user.user_type == 'RT':
            queryset = MicroBulkOrderProducts.objects.all()
        elif request.user.user_type == 'CM':
            queryset = MicroBulkOrderProducts.objects.filter(customer=request.user)
        serializer = MicroBulkOrderProductsSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = MicroBulkOrderProductsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MicroBulkOrderProductsDetails(APIView):
    permission_classes = [GenericAuth]

    def get_microbulkorderproduct_obj(self, id):
        return get_object_or_404(MicroBulkOrderProducts, id=id)

    def get(self, request, id):
        queryobj = self.get_microbulkorderproduct_obj(id)
        serializer = MicroBulkOrderProductsSerializer(queryobj)
        if serializer:
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        queryobj = self.get_microbulkorderproduct_obj(id)
        serializer = MicroBulkOrderProductsSerializer(queryobj, data=request.data)
        if serializer.is_valid():
            if request.user.user_type == 'SF':
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        obj = self.get_microbulkorderproduct_obj(id)
        if request.user.is_staff:
            obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
