from django.db import models


# Create your models here.
class CustomerQuery(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=300, default=" ")
    created_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
