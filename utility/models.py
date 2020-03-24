from django.db import models
from django.contrib.gis.db import models

# Create your models here.
from simple_history.models import HistoricalRecords
from bases.models import BaseModel
from userProfile.models import UserProfile


class Area(BaseModel): #write serializer
    area_name=models.CharField(max_length=200)
    polygon = models.PolygonField()
    history = HistoricalRecords()

    def __str__(self):
        return self.area_name


class CityCountry(BaseModel): #write serializer
    tire_city = models.CharField(max_length=200)
    tire_country=models.CharField(max_length=200)
    history = HistoricalRecords()

    def __str__(self):
        return self.tire_city + self.tire_country


class Location(BaseModel):
    geo_loc = models.PointField()
    loc_name = models.CharField(max_length=200)
    city_country = models.ForeignKey(CityCountry,on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return self.loc_name


class ProductUnit(BaseModel):
    product_unit = models.CharField(max_length=10,unique=True)
    product_unit_bn = models.CharField(max_length=10,unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.product_unit

    class Meta:
        verbose_name = 'Product Unit'
        verbose_name_plural = 'Product Unit'


class Remarks(BaseModel):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,blank=True,null=True)
    remark = models.CharField(max_length=400)

    def __str__(self):
        return self.user


