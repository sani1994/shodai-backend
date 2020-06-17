from django.db import models

# Create your models here.
from simple_history.models import HistoricalRecords

from bases.models import BaseModel
from product.models import Product
from retailer.models import Shop


class ShopInventory(BaseModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # stock_balance = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    incoming = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    outgoing = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    debit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # money_balance= models.DecimalField(max_digits=8,decimal_places=2,default=0)
    history = HistoricalRecords()

    @property
    def stock_balance(self):
        self.stock_balance = self.stock_balance + self.incoming
        self.stock_balance = self.stock_balance - self.outgoing

        return self.stock_balance

    @property
    def money_balance(self):
        self.money_balance = self.money_balance + self.credit
        self.money_balance = self.money_balance - self.debit

        return self.money_balance


class ShopInventoryHistory(BaseModel):  # write serializer
    shop_history = ShopInventory()
