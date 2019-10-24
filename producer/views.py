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
            
        serializer = ProducerProductSerializer(producer,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = ProducerProductSerializer(data=request.data)
        if request.user.user_type== 'SF':
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
    def get_producerProduct_object(self,id):
        obj = ProducerProduct.objects.filter(id=id).first()

    def get(self, request, id, format=None):
        producer = self.get_producerProduct_object( id)
        serializer = ProducerProductSerializer(producer)
        if serializer:
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        producer = self.get_producerProduct_object(id)
        serializer = ProducerProductSerializer(producer, data=request.data)
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