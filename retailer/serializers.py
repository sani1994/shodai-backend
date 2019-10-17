from retailer.models import  Account, Shop
from rest_framework import serializers


# class RetailerSerializer(serializers.HyperlinkedModelSerializer):
#     user = serializers.HyperlinkedRelatedField(
#         # many=True,
#         read_only=True,
#         view_name='user'
#     )    # foreignKey
#     address = serializers.HyperlinkedRelatedField(
#         # many=True,
#         read_only=True,
#         view_name='address'
#     ) # foreignKey
#     # retailer_logo = serializers.SerializerMethodField()
#     # retailer_email = serializers.EmailField(max_length=20)
#     # retailer_website = serializers.CharField(max_length=20)
#
#     def create(self, validated_data):
#         return Retailer(**validated_data)
#
#     def update(self, instance, validated_data):
#         instance.user = validated_data.get('user', instance.user)
#         instance.address = validated_data.get('address', instance.address)
#         instance.retailer_logo = validated_data.get('retailer_logo', instance.retailer_logo)
#         instance.retailer_email = validated_data.get('retailer_email', instance.retailer_email)
#         instance.retailer_website = validated_data.get('retailer_website', instance.retailer_website)
#         return instance
#
#     def get_retailer_logo(self, retailer):
#         request = self.context.get('request')
#         retailer_logo = retailer.retailer_logo.url
#         return request.build_absolute_uri(retailer_logo)
#
#     class Meta:
#         model = Retailer
#         fields = ['user', 'address', 'retailer_logo', 'retailer_email', 'retailer_website']




class AccountSerializer(serializers.HyperlinkedModelSerializer):
    # retailer_id = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='reatailer_id'
    # ) # foreignKey
    # bank_name = serializers.CharField(max_length=200)
    # account_no = serializers.IntegerField()
    # account_name = serializers.CharField(max_length=50)

    def create(self, validated_data):
        return Account(**validated_data)

    def update(self, instance, validated_data):
        # instance.retailer_id = validated_data.get('retailer_id', instance.retailer_id)
        instance.bank_name = validated_data.get('bank_name', instance.bank_name)
        instance.account_no = validated_data.get('account_no', instance.account_no)
        instance.account_name = validated_data.get('account_name', instance.account_name)
        return instance

    class Meta:
        model = Account
        fields = [ 'id','user_id', 'bank_name ', 'account_no', 'account_name']
#

class ShopSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        print(user)
        return Shop.objects.create(**validated_data,created_by= user,user=user)

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
        instance.save()
        return  instance

    class Meta:
        model = Shop
        fields = '__all__'
