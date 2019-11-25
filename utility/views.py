from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView

from sodai.utils.permission import GenericAuth
from utility.models import Area


class AreaList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        queryset = Area.objects.all()
