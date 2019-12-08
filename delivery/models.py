from django.db import models

# Create your models here.
from simple_history.models import HistoricalRecords

from bases.models import BaseModel
from producer.models import ProducerBulkRequest
from product.models import Product
from retailer.models import AcceptedOrder
from userProfile.models import UserProfile
import random


class DeliveryCheckList(BaseModel):
    producer_bulk_request = models.ForeignKey(ProducerBulkRequest,on_delete=models.CASCADE,null=True,blank=True)
    assigned_user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    retailer_accept_order = models.ForeignKey(AcceptedOrder,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20,default=None)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class DeliveryCheckListItem(BaseModel):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    handed_over_to = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    delivery_check_list = models.ForeignKey(DeliveryCheckList, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_checked = models.BooleanField(default=False)
    image = models.ImageField(upload_to='delivery/checkListItem',blank= True,null=True)
    is_approved = models.BooleanField(default=False)
    first_level_qty = models.DecimalField(decimal_places=2,max_digits=5)
    second_level_qty = models.DecimalField(decimal_places=2, max_digits=5)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class DeliveryCheckListTemplate(BaseModel):
    delivery_check_list = models.ForeignKey(DeliveryCheckList, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_checked = models.BooleanField(default=False)
    image = models.ImageField(upload_to='delivery/checkListItemTemplate', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    history = HistoricalRecords()





