from django.shortcuts import render
from producer.serializers import ProducerFarmSerializer, ProducerProductSerializer

from producer.models import ProducerProduct, ProducerFarm

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

# Create your views here.


class ProducerProductList(APIView):

    ## list of Producer

    def get(self, request, format=None):
        is_staff = request.user.is_staff
        producer = ProducerProduct.objects.all()
        # if is_staff:
        #     producer = ProducerProduct.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         producer = ProducerProduct.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         producer = ProducerProduct.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         producer = ProducerProduct.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        serializer = ProducerProductSerializer(producer, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProducerProductSerializer(data=request.data)
        if request.user.is_staff:
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if request.user.user_type=='PD': # Producer = PD
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProducerProductDetail(APIView):
    """
    Retrieve, update and delete Producer
    """
    def get_object(self, request, pk):
        is_staff = request.user.is_staff
        try:
            if is_staff:
                return ProducerProduct.objects.get(pk=pk)
            else:
                user_type = request.user.user_type
                if user_type=='CM':  # Customer = CM
                    return ProducerProduct.objects.get(pk=pk)
                elif user_type=='RT': # Retailer = RT
                    return ProduceProduct.objects.get(pk=pk)
                    # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                elif user_type== 'PD': # Producer = PD
                    return ProducerProduct.objects.get(pk=pk)
                     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                return ProducerProduct.objects.get(pk=pk)
        except ProducerProduct.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        producer = self.get_object(request, pk)
        serializer = ProducerProductSerializer(producer, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        producer = self.get_object(request, pk)
        serializer = ProducerProductSerializer(producer, data=request.data)
        if serializer.is_valid():
            if request.user.is_staff:
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        producer = self.get_object(request, pk)
        if request.user.is_staff:
            producer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    

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
            
        serializer = ProducerFarmSerializer(producer, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProducerFarmSerializer(data=request.data)
        if request.user.is_staff:
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
    def get_object(self, request, pk):
        is_staff = request.user.is_staff
        try:
            if is_staff:
                return ProducerFarm.objects.get(pk=pk)
            else:
                user_type = request.user.user_type
                if user_type=='CM':  # Customer = CM
                    return ProducerFarm.objects.get(pk=pk)
                elif user_type=='RT': # Retailer = RT
                    return ProducerFarm.objects.get(pk=pk)
                    # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                elif user_type== 'PD': # Producer = PD
                    return ProducerFarm.objects.get(pk=pk)
                     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                return ProducerFarm.objects.get(pk=pk)
        except ProducerFarm.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        ProducerFarmDetail = self.get_object(request, pk)
        serializer = ProducerFarmSerializer(producer, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        ProducerFarmDetail = self.get_object(request, pk)
        serializer = ProducerFarmSerializer(producer, data=request.data)
        if serializer.is_valid():
            if request.user.is_staff:
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        producer_farm = self.get_object(request, pk)
        if request.user.is_staff:
            ProducerFarmDetail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)