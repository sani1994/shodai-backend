from django.contrib import admin
from material.admin.sites import site

# Register your models here.
from delivery.models import DeliveryCheckList, DeliveryCheckListItem, DeliveryCheckListTemplate

site.register(DeliveryCheckList)
site.register(DeliveryCheckListItem)
site.register(DeliveryCheckListTemplate)
