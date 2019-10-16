from retailer.models import  Retailer,Account
from rest_framework import serializers


class RetailerSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
        # many=True,
        read_only=True,
        view_name='user'
    )    # foreignKey
    address = serializers.HyperlinkedRelatedField(
        # many=True,
        read_only=True,
        view_name='address'
    ) # foreignKey
    # retailer_logo = serializers.SerializerMethodField()
    # retailer_email = serializers.EmailField(max_length=20)
    # retailer_website = serializers.CharField(max_length=20)

    def create(self, validated_data):
        return Retailer(**validated_data)

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.address = validated_data.get('address', instance.address)
        instance.retailer_logo = validated_data.get('retailer_logo', instance.retailer_logo)
        instance.retailer_email = validated_data.get('retailer_email', instance.retailer_email)
        instance.retailer_website = validated_data.get('retailer_website', instance.retailer_website)
        return instance

    def get_retailer_logo(self, retailer):
        request = self.context.get('request')
        retailer_logo = retailer.retailer_logo.url
        return request.build_absolute_uri(retailer_logo)

    class Meta:
        model = Retailer
        fields = ['user', 'address', 'retailer_logo', 'retailer_email', 'retailer_website']




class AccountSerializer(serializers.HyperlinkedModelSerializer):
    retailer_id = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='reatailer_id'
    ) # foreignKey
    bank_name = serializers.CharField(max_length=200)
    account_no = serializers.IntegerField()
    account_name = serializers.CharField(max_length=50)

    def create(self, validated_data):
        return Account(**validated_data)

    def update(self, instance, validated_data):
        instance.retailer_id = validated_data.get('retailer_id', instance.retailer_id)
        instance.bank_name = validated_data.get('bank_name', instance.bank_name)
        instance.account_no = validated_data.get('account_no', instance.account_no)
        instance.account_name = validated_data.get('account_name', instance.account_name)
        return instance

    class Meta:
        model = Account
        fields = [ 'retailer_id', 'bank_name ', 'account_no', 'account_name']
#
