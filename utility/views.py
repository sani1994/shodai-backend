from django.shortcuts import render, get_object_or_404
from httplib2 import Response
from rest_framework.views import APIView
from sodai.utils.permission import GenericAuth
from utility.models import Area, ProductUnit, Remarks
from utility.serializers import AreaSerializer, ProductUnitSerializer, RemarksSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


class AreaList(APIView):                #get area list and create area
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


class AreaDetails(APIView):         # area object get, update and delete
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

    def delete(self, request, id):
        if request.user.is_staff:
            obj = self.get_area_obj(id)
            obj.delete()
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductUnitList(APIView):         # product unit list get and create
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = ProductUnit.objects.all()

        serializer = ProductUnitSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.user.is_staff:
            if not ProductUnit.objects.filter(ProductUnit_Item__contains=request.data):
                serializer = ProductUnitSerializer(data=request.data)
                if serializer.is_valid():
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
        return Response({'Duplicat data: '+ str(request.data['product_unit'])}, status=status.HTTP_400_BAD_REQUEST)


class ProductUnitDetails(APIView):          #product unit object get, update and delete
    permission_classes = [GenericAuth]

    def get_productunit_obj(self, id):
        obj = get_object_or_404(ProductUnit, id=id)
        return obj

    def get(self, request, id):
        if request.user.is_staff:
            obj = self.get_productunit_obj(id)
            serializer = ProductUnitSerializer(obj)
            if serializer:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, id):
        if request.user.is_staff:
            obj = self.get_productunit_obj(id)
            serializer = ProductUnitSerializer(obj, data=request.data)
            if serializer:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        if request.user.is_staff:
            obj = self.get_productunit_obj(id)
            if obj:
                obj.delete()
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class RemarksList(APIView):             #get remarks list and create area

    permission_classes = [GenericAuth]

    def get(self,request):
         queryset = Remarks.objects.all()
         serializer = RemarksSerializer(queryset, many=True)
         if serializer:
             return Response(serializer.data, status=status.HTTP_200_OK)
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = RemarksSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemarksDetails(APIView):              #remarks unit object get, update and delete
    permission_classes = [GenericAuth]

    def get_remarks_obj(self,id):
        return get_object_or_404(Remarks,id=id)

    def get(self,request,id):
        obj = self.get_remarks_obj(id)
        serializer = RemarksSerializer(obj)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,id):
        obj = self.get_remarks_obj(id)
        serializer = RemarksSerializer(obj,data=request.data,context={'request',request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if request.user.is_staff:
            obj = self.get_remarks_obj(id)
            obj.delete()
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)



