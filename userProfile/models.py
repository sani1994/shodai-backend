import qrcode
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone 

# from bases.models import BaseModel
# Create your models here.


class UserProfile(AbstractUser):
    CUSTOMER = 'CM'
    RETAILER = 'RT'
    PRODUCER = 'PD'
    STAFF = 'SF'
    USER_TYPES_CHOICES = [
        (CUSTOMER, 'Customer'),
        (RETAILER, 'Retailer'),
        (PRODUCER, 'Producer'),
        (STAFF, 'Staff')
    ]
    user_type = models.CharField(max_length=30, choices=USER_TYPES_CHOICES, default=CUSTOMER)
    user_image = models.ImageField(upload_to='user/%Y/%m/%d',blank=True,null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True,unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True,unique=True)
    user_NID = models.CharField(max_length=100,blank=True,null=True,unique=True)
    ref_code = models.CharField(max_length=10, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_on = timezone.now()
        # self.modified = timezone.now()
        return super(UserProfile, self).save(*args, **kwargs)


class Address(models.Model):

    road = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    district = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    zip_code = models.CharField(max_length=30, blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return "{}, {}, {}".format(self.road, self.city, self.district)


class Otp(models.Model):

     mobile_number = models.CharField(max_length=11,unique=True)
     otp_code = models.CharField(max_length=10,blank=True,null=True)
     count = models.IntegerField(default=0,help_text='Number of otp sent')

     def __str__(self):
         return str(self.mobile_number) + 'is sent' + str(self.otp_code)


class BlackListedToken(models.Model):
    token = models.CharField(max_length=1000, unique=True)
    user = models.ForeignKey(
        UserProfile, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "BlackListed Tokens"

