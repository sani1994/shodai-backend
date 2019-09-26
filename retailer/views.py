from django.shortcuts import render
from retailer.serializers import RetailerSerializer, AccountSerializer
from retailer.models import Retailer, Account

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
# Create your views here.



class RetailerList(APIView):

    ## list of Retailer

    def get(self, request, format=None):
        is_staff = request.user.is_staff
        retailer = Retailer.objects.all()
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
            
        serializer = RetailerSerializer(retailer, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RetailerSerializer(data=request.data)
        if request.user.is_staff:
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if request.user.user_type=='RT': # Retailer = RT
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class RetailerDetail(APIView):
    """
    Retrieve, update and delete Orders
    """
    def get_object(self, request, pk):
        is_staff = request.user.is_staff
        try:
            if is_staff:
                return Retailer.objects.get(pk=pk)
            else:
                user_type = request.user.user_type
                if user_type=='CM':  # Customer = CM
                    return Retailer.objects.get(pk=pk)
                elif user_type=='RT': # Retailer = RT
                    return Retailer.objects.get(pk=pk)
                    # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                elif user_type== 'PD': # Producer = PD
                    return Retailer.objects.get(pk=pk)
                     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                return Retailer.objects.get(pk=pk)
        except Retailer.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        retailer = self.get_object(request, pk)
        serializer = RetailerSerializer(retailer, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        retailer = self.get_object(request, pk)
        serializer = RetailerSerializer(retailer, data=request.data)
        if serializer.is_valid():
            if request.user==Retailer.created_by or request.user.is_staff:
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        retailer = self.get_object(request, pk)
        if request.user.is_staff:
            retailer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  



class AccountList(APIView):

    ## list of Retailer' Account

    def get(self, request, format=None):
        is_staff = request.user.is_staff
        account = Account.objects.all()
        # if is_staff:
        #     account = Account.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         account = Account.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         aroduct = Account.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         account = Account.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        serializer = AccountSerializer(account, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AccountSerializer(data=request.data)
        if request.user.is_staff:
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if request.user.user_type=='RT': # Retailer = RT
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class AccountDetail(APIView):
    """
    Retrieve, update and delete Orders
    """
    def get_object(self, request, pk):
        is_staff = request.user.is_staff
        try:
            if is_staff:
                return Account.objects.get(pk=pk)
            else:
                user_type = request.user.user_type
                if user_type=='CM':  # Customer = CM
                    return Account.objects.get(pk=pk)
                elif user_type=='RT': # Retailer = RT
                    return Account.objects.get(pk=pk)
                    # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                elif user_type== 'PD': # Producer = PD
                    return Account.objects.get(pk=pk)
                     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                return Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        account = self.get_object(request, pk)
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        account = self.get_object(request, pk)
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid():
            if request.user==Account.created_by or request.user.is_staff:
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        account= self.get_object(request, pk)
        if request.user.is_staff:
            account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  






