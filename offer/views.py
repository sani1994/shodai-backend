from django.shortcuts import render
from rest_framework.generics import get_object_or_404

from offer.models import Offer,OfferProduct
from offer.serializers import OfferSerializer, OfferProductSerializer, OfferProductReadSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
from sodai.utils.permission import GenericAuth


class OfferList(APIView):
    permission_class= [GenericAuth,]

    def get(self,request):
        if request.user.is_staff:
            queryset = Offer.objects.all()
        queryset=Offer.objects.filter(is_approved=True)
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
                serializer = OfferSerializer(data=request.data,context={'request':request})
                if serializer.is_valid():
                    serializer.save(created_by = request.user)
                    return Response (serializer.data,status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"status": "Invalid serializer"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
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
                    return Response({"status": "Invalid serializer"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "Status": "No content",
                    "details": "Content not available"
                }, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self,request,id):
        if request.user.user_type == 'SF':
            obj = self.get_object(id)
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
        if request.user.is_staff:
            queryset = OfferProduct.objects.all()
        queryset=OfferProduct.objects.filter(is_approved = True)
        if queryset:
            serializer = OfferProductReadSerializer(queryset,many=True)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Invalid serializer"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        if request.user.user_type== 'SF' and  request:
            serializer = OfferProductSerializer(data= request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request or No content"}, status=status.HTTP_403_FORBIDDEN)


class OfferProductDetail(APIView):

    def get_offerproduct_obj(self,id):
        obj = OfferProduct.objects.filter(id=id).first()
        return  obj

    def get(self,request,id):
        obj = self.get_offerproduct_obj(id)
        if obj:
            serializer = OfferProductReadSerializer(obj)
            # offerProductList = obj.offerproduct_set.all()
            # serializer = OfferProductSerializer(offerProductList)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Invalide serializer"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        obj = self.get_offerproduct_obj(id)
        if obj:
            serializer = OfferProductSerializer(obj,data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by = request.user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)

    def delete(self,request,id):
        obj = self.get_offerproduct_obj(id)
        if obj:
            obj.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)


class GetOfferProducts(APIView):

    permission_classes = [GenericAuth]

    def get(self,request,id):
        obj = get_object_or_404(Offer,id=id)
        offerProducts = []
        offerserializer = OfferSerializer(obj)
        offerProductList = obj.offerproduct_set.all()
        offerProductserializer = OfferProductReadSerializer(offerProductList,many=True)
        if offerserializer and  offerProductserializer:
            # offerProductsData = offerProductserializer.data
            for data in offerProductserializer.data:
                product = data['product']
                product['offer_price']=data['offer_price']
                product['offer_product_balance']=data['offer_product_balance']
                # product['offer_id'] = data['offer']['id']
                # product['offer_name'] = data['offer'] ['offer_name']
                # product['product_id'] = data['product']['id']
                # product['product_name'] = data['product']['product_name']
                # product['product_name_bn'] = data['product']['product_name_bn']
                # product['product_image'] = data['product']['product_image']
                # product['product_description'] = data['product']['product_description']
                # product['product_unit'] = data['product']['product_unit']
                # product['product_price'] = data['product']['product_price']
                offerProducts.append(product)
            offerdetail=offerserializer.data
            offerdetail['offer_products']=offerProducts
            return Response(offerProducts, status=status.HTTP_200_OK) # returning on offer product list
        else:
            return Response(offerserializer.errors, status=status.HTTP_400_BAD_REQUEST)

