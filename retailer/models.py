from django.db import models
from userProfile.models import UserProfile
from userProfile.models import Address
from bases.models import BaseModel
# Create your models here.

class Retailer(BaseModel):
    user = models.ForeignKey(UserProfile, models.SET_NULL,
    blank=True,
    null=True)
    address = models.ForeignKey(Address, models.SET_NULL,
    blank=True,
    null=True)
    retailer_logo = models.ImageField(blank=True, null=True)
    retailer_email = models.EmailField(max_length=20, blank=True, null=True)
    retailer_website = models.CharField(max_length=20, blank=True, null=True)


class Account(BaseModel):
    retailer_id = models.ForeignKey(Retailer, models.SET_NULL,
    blank=True,
    null=True)
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    account_no = models.IntegerField(blank=True, null=True)
    account_name = models.CharField(max_length=50, blank=True, null=True)



