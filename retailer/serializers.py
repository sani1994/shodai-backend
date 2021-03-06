from retailer.models import Account, Shop, AcceptedOrder, ShopProduct
from rest_framework import serializers
from product.serializers import RetailerProductSerializer


class AccountSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user= self.context['request'].user
        return Account.objects.create(**validated_data,user=user)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.bank_name = validated_data.get('bank_name', instance.bank_name)
        instance.account_no = validated_data.get('account_no', instance.account_no)
        instance.account_name = validated_data.get('account_name', instance.account_name)
        instance.user = user
        instance.save()
        return instance

    class Meta:
        model = Account
        fields = [ 'id', 'user_id', 'bank_name', 'account_no', 'account_name']
        depth = 1


class ShopSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        return Shop.objects.create(**validated_data,user=user)

    def update(self, instance, validated_data):
        user = self.context['request'].user

        instance.shop_name = self.validated_data.get('shop_name',instance.shop_name)
        instance.shop_lat = self.validated_data.get('shop_lat',instance.shop_lat)
        instance.shop_long = self.validated_data.get('shop_long',instance.shop_long)
        instance.shop_address = self.validated_data.get('shop_address',instance.shop_address)
        instance.shop_image = self.validated_data.get('shop_image',instance.shop_image)
        instance.shop_licence = self.validated_data.get('shop_licence',instance.shop_licence)
        instance.shop_website = self.validated_data.get('shop_website',instance.shop_website)
        instance.user = user
        instance.modified_by = user
        instance.is_approved = False
        instance.save()
        return  instance

    class Meta:
        model = Shop
        fields = '__all__'


class AcceptedOrderSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        return AcceptedOrder.objects.create(**validated_data,user=user)

    class Meta:
        model=AcceptedOrder
        fields= '__all__'


class AcceptedOrderReadSerializer(serializers.ModelSerializer):

    class Meta:
        model=AcceptedOrder
        fields= '__all__'
        depth = 1


#########
class ShopProductSerializer(serializers.ModelSerializer):

    # product = RetailerProductSerializer(read_only=True)

    # def create(self, validated_data):
    #     shop = Shop.objects.get(user= self.context['request'].user)
    #     return ShopProduct.objects.create(shop=shop, **validated_data,created_by = self.context['request'].user)

    def update(self, instance, validated_data):
        return ShopProduct.objects.update(instance, **validated_data, modified_by = self.context['request'].user)

    class Meta:
        model = ShopProduct
        # fields = ('id','product','shop','product_image','product_unit','product_price','product_stock')
        fields = '__all__'

class ShopProductGetSerializer(serializers.ModelSerializer):

    # product = RetailerProductSerializer(read_only=True)
    # product_unit = ProductUnitSerializer(read_only=True)

  
    class Meta:
        model = ShopProduct
        fields = ('id', 'user', 'product', 'shop', 'product_image', 'product_unit_name', 'product_name', 'product_name_bn', 'product_description', 'product_description_bn', 'product_price', 'product_stock')
        # fields = ('__all__')
