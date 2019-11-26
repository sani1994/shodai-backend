from django.shortcuts import render, get_object_or_404
from httplib2 import Response
from rest_framework.views import APIView
from sodai.utils.permission import GenericAuth
from utility.models import Area
from utility.serializers import AreaSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


class AreaList(APIView):
    permission_classes = [GenericAuth]

    def get(self,request):
        queryset = Area.objects.all()
        serializer = AreaSerializer(queryset,many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        serializer = AreaSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class AreaDetails(APIView):
    permission_classes = [GenericAuth]

    def get_area_obj(self,id):
        return get_object_or_404(Area,id=id)

    def get(self,request,id):
        obj = self.get_area_obj(id)
        serializer = AreaSerializer(obj)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,id):
        obj = self.get_area_obj(id)
        serializer = AreaSerializer(obj,data=request.data,context={'request',request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




