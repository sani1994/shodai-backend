from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from httplib2 import Response

from userProfile.models import UserProfile, Address
from rest_framework import serializers
from django.db.models import Q


class UserProfileSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.mobile_number = validated_data.get('mobile_number', instance.mobile_number)
        instance.user_image = validated_data.get('user_image',instance.user_image)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.ref_code = validated_data.get('ref_code', instance.ref_code)
        instance.pin_code = validated_data.get('pin_code', instance.pin_code)
        instance.password = validated_data.get('password',instance.password)
        return instance
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        write_only_fields = ('password',)


    def create(self,validated_data):
        user = UserProfile.objects.create(
        user_type = validated_data['user_type'],
        mobile_number=validated_data['mobile_number'],
        first_name = validated_data['first_name'],
        last_name = validated_data['last_name'],
        email = validated_data['email'],
        # ref_code = validated_data['ref_code'],
        # pin_code = validated_data['pin_code'],
        # crated_on = validated_data['create_on'],
        # modified_on = validated_data['modified_on']
        )
        if user:
            user.set_password(validated_data['password'])
            user.save()
        return user






class AddressSerializer(serializers.ModelSerializer):
    # road = serializers.CharField(max_length=30)
    # city = serializers.CharField(max_length=30)
    # district = serializers.CharField(max_length=30)
    # country = serializers.CharField(max_length=30)
    # zip_code = serializers.CharField(max_length=30)
    # user = serializers.RelatedField(
    #     many=True,
    #     read_only=True,
    #     # view_name='user'
    # ) # foreignKey
    # user = serializers.CharField()


    def create(self, validated_data):
        user= self.context['request'].user.id
        # user=validated_data.pop('user')
        user_instance = UserProfile.objects.filter(id=user).first()
        return Address.objects.create(**validated_data,user=user_instance)

    def update(self, instance, validated_data):
        instance.road = validated_data.get('road', instance.road)
        instance.city = validated_data.get('city', instance.city)
        instance.district = validated_data.get('district', instance.district)
        instance.country = validated_data.get('country', instance.country)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance
    
    
    class Meta:
        model = Address
        fields = ['id','road', 'city', 'district', 'country', 'zip_code','user_id']
        depth = 1


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        if not validated_data:
            return Response({'Error': "Invalid Data"})
        user = UserProfile.objects.create(
            user_type= validated_data['user_type'],
            username=validated_data['mobile_number'],
            user_image=validated_data['user_image'],
            mobile_number = validated_data['mobile_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        if user:
            user.set_password(validated_data['password'])
            user.save()
        return user

    class Meta:
        model=UserProfile
        fields= ('user_type','mobile_number','user_image','first_name','last_name','email','password')


class RetailerRegistrationSreializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = self.context['request'].user

        if not validated_data:
            return Response({'Error': "Invalid Data"})
        user = UserProfile.objects.create(
            user_type= validated_data['user_type'],
            mobile_number = validated_data['mobile_number'],
            username = validated_data['mobile_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            user_image=validated_data['user_image'],
            user_NID=validated_data['user_NID'],
        )
        if user:
            user.set_password(validated_data['password'])
            user.save()
        return user

    class Meta:
        model = UserProfile
        fields = ('id','user_type','user_image','mobile_number','first_name','last_name','email','user_NID','password')