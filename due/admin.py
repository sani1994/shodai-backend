from django.contrib import admin
from material.admin.sites import site

# Register your models here.
from due.models import UserDues

site.register(UserDues)
