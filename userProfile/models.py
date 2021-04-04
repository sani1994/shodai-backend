import qrcode
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# from bases.models import BaseModel
# Create your models here.
from simple_history.models import HistoricalRecords


class UserProfile(AbstractUser):
    '''
    Add the following boolean fields                    # this changes not implemented yet.
    is_customer: if customer then True                  # should add this following fields for further enhanhment
    is_retailer: if retailer then True
    is_producer: if producer then True
    is_sales: if staff then True
    is_delivery: if staff then True
    is_third_party: defaults to False
    '''
    CUSTOMER = 'CM'
    RETAILER = 'RT'
    PRODUCER = 'PD'
    STAFF = 'SF'
    VENDOR = 'VN'
    USER_TYPES_CHOICES = [
        (CUSTOMER, 'Customer'),
        (RETAILER, 'Retailer'),
        (PRODUCER, 'Producer'),
        (STAFF, 'Staff'),
        (VENDOR, 'Vendor')
    ]
    user_type = models.CharField(max_length=30, choices=USER_TYPES_CHOICES, default=CUSTOMER)
    user_image = models.ImageField(upload_to='user/%Y/%m/%d',blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    user_NID = models.CharField(max_length=100,blank=True,null=True, unique=True)
    ref_code = models.CharField(max_length=10, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_retailer = models.BooleanField(default=False)
    is_producer = models.BooleanField(default=False)
    is_sales = models.BooleanField(default=False)
    is_delivery = models.BooleanField(default=False)
    is_third_party = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_valid_till = models.DateTimeField(blank=True, null=True)
    pin_verified = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_on = timezone.now()
            if self.user_type == 'RT':
                self.is_retailer = True
            if self.user_type == 'PD':
                self.is_producer = True
            return super(UserProfile, self).save(*args, **kwargs)
        if self.user_type == 'RT':
            self.is_retailer = True
        if self.user_type == 'PD':
            self.is_producer = True
        return super(UserProfile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profile'


class Address(models.Model):
    road = models.CharField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    district = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    zip_code = models.CharField(max_length=30, blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return self.road


class Otp(models.Model):
    mobile_number = models.CharField(max_length=11, unique=True)
    otp_code = models.CharField(max_length=10, blank=True, null=True)
    count = models.IntegerField(default=0, help_text='Number of otp sent')
    history = HistoricalRecords()

    def __str__(self):
        return str(self.mobile_number) + 'is sent' + str(self.otp_code)


class BlackListedToken(models.Model):
    token = models.CharField(max_length=1000, unique=True)
    user = models.ForeignKey(
        UserProfile, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "BlackListed Tokens"
