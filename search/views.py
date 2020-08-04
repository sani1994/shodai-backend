import operator
from functools import reduce

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
from rest_framework.views import APIView
from rest_framework_elasticsearch import es_views, es_filters

from product.serializers import ProductSerializer
from search.document import ProductDocument
from search.serializers import ElasticSearchProductSerializer
from elasticsearch_dsl.query import Q


class Search(APIView):
    def get(self, request):
        q = self.request.query_params.get('q')
        products = []
        if q:
            product1 = ProductDocument.search().query("match", product_name=q)
            product2 = ProductDocument.search().filter(
                'nested',
                path='product_meta',
                query=Q('match', product_meta__name=q)
            )
            serializer1 = ElasticSearchProductSerializer(product1, many=True)
            products.append(serializer1.data)
            serializer2 = ElasticSearchProductSerializer(product2, many=True)
            products.append(serializer2.data)
            return Response(products, status=status.HTTP_200_OK)
        product = ""
        return Response(product, status=status.HTTP_204_NO_CONTENT)

# def search(request):
#     if request.method == "GET":
#         q = request.GET.get('q')
#         if q:
#             product = ProductDocument.search().query("match", product_name = q)
#             return render(request, 'search.html', {'product': product})
#         product = ""
#
#         return render(request,'search.html', {'product': product})


# class Search(es_views.ListElasticAPIView):
#
#     def get(self, request):
#         q = request.data['q']
#         es_model = BlogIndexes_filter_backends = (es_filters.ElasticFieldsFilter, es_filters.ElasticSearchFilter)
#         es_filter_fields = (es_filters.ESFieldFilter('product_name'),)
#         es_search_fields = ('product_name')
#         if q:
#             product = es_search_fields.find(q)
#             print(product)
#             serializer = ElasticSearchProductSerializer(product)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         product = ""
#         return  Response(product, status=status.HTTP_204_NO_CONTENT)
