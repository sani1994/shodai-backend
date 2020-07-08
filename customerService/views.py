from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from customerService.models import CustomerQuery
from customerService.serializers import CustomerQuerySerializer


class CustomerQueryList(APIView):

    def get(self, request):

        queryset = CustomerQuery.objects.all()
        if queryset:
            serializer = CustomerQuerySerializer(queryset, many=True)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)