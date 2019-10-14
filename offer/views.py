from django.shortcuts import render
from offer.models import Offer,OfferProduct
from offer.serializers import OfferSerializer,OfferProductSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
from sodai.utils.permission import GenericAuth


class OfferList(APIView):
    permission_class= [GenericAuth,]

    def get(self,request):
        queryset = Offer.objects.all()
        print(queryset)
        if queryset:
            serializer = OfferSerializer(queryset,many=True)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"},status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        if request.user.user_type == 'SF':
            if request.data:
                serilaizer = OfferSerializer(data=request.data)
                if serilaizer.is_valid():
                    serilaizer.save(created_by = request.user)
                    return Response (serilaizer.data,status=status.HTTP_201_CREATED)
                else:
                    return Response(serilaizer.error_messages,status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response ({"status": "Unauthorized request"},status=status.HTTP_403_FORBIDDEN)


class OfferDetails(APIView):

    permission_classes = [GenericAuth]

    def get_object(self, id):
        return Offer.objects.filter(id = id).first()

    def get(self,request,id):
        obj = self.get_object(id)
        if obj:
            serializer = OfferSerializer(obj)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Invalide serializer"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Rontent not available"
            }, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        if request.user.user_type == 'SF':
            obj = self.get_object(id)
            if obj:
                serializer = OfferSerializer(obj,data=request.data)
                if serializer.is_valid():
                    serializer.save(modified_by = request.user)
                    return Response(serializer.data,status= status.HTTP_200_OK)
                else:
                    return Response({"status": "Invalide serializer"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "Status": "No content",
                    "details": "Rontent not available"
                }, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self,request,id):
        if request.user.user_type == 'SF':
            obj =  self.get_object(id)
            if obj:
                obj.delete()
                return Response ({"status": "Delete successful..!!"},status=status.HTTP_200_OK)
            else:
                return Response({
                    "Status": "No content",
                    "details": "Content not available"
                }, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class OfferProductList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        queryset = OfferProduct.objects.all()
        if queryset:
            serializer = OfferProductSerializer(queryset)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Invalide serializer"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        # if request.user.user_type== 'RT' and  request:
            print(request.user.user_type)
            serializer = OfferProductSerializer(data= request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
            # else:
            #     return Response({"status": "Unauthorized request or No content"}, status=status.HTTP_403_FORBIDDEN)