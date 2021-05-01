from django.db import models

# Create your models here.
from simple_history.models import HistoricalRecords

from base.models import BaseModel
from retailer.models import Shop
from user.models import UserProfile


class UserDues(BaseModel): #write serializer
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    credit = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    history = HistoricalRecords()

    @property
    def money_balance(self):
        self.money_balance = self.money_balance + self.credit
        self.money_balance = self.money_balance - self.debit

        return self.money_balance


class UserDuesHistory(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,blank=True,null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE,blank=True,null=True)
    debit = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    credit = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    # user_dues_history = UserDues()