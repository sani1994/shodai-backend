from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from base.models import BaseModel
from user.models import UserProfile


class Area(BaseModel):
    area_name = models.CharField(max_length=200)
    polygon = models.PolygonField()
    history = HistoricalRecords()

    def __str__(self):
        return self.area_name


class DeliveryZone(BaseModel):
    zone = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.zone


class CityCountry(BaseModel):
    tire_city = models.CharField(max_length=200)
    tire_country = models.CharField(max_length=200)
    history = HistoricalRecords()

    def __str__(self):
        return self.tire_city + self.tire_country


class Location(BaseModel):
    geo_loc = models.PointField()
    loc_name = models.CharField(max_length=200)
    city_country = models.ForeignKey(CityCountry, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return self.loc_name


class ProductUnit(BaseModel):
    product_unit = models.CharField(max_length=10, unique=True)
    product_unit_bn = models.CharField(max_length=10, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.product_unit

    class Meta:
        verbose_name = 'Product Unit'
        verbose_name_plural = 'Product Unit'


class Remarks(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
    remark = models.CharField(max_length=400)

    def __str__(self):
        return self.user


class Message(BaseModel):
    message = models.CharField(max_length=300)
    time = models.TimeField()
    action = models.BooleanField(default=False)
    screen_name = models.CharField(max_length=300)

    def __str__(self):
        return self.message


class Banner(BaseModel):
    banner_heading = models.CharField(max_length=100)
    banner_img = models.ImageField(upload_to="pictures/banner", verbose_name="Image: 1300px X 300px")
    banner_show_starts_in = models.DateTimeField()
    banner_show_ends_in = models.DateTimeField()
    banner_url = models.CharField(max_length=300, blank=True, null=True)
    offer = models.ForeignKey('offer.Offer', models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.banner_heading
