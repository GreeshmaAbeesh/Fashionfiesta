from django.db import models

# Create your models here.
class Custom(models.Model):
    
    address_line_1 = models.CharField(blank=True,max_length=100)
    address_line_2 = models.CharField(blank=True,max_length=100)
    profile_picture = models.ImageField(blank=True,upload_to='userprofile/')
    city = models.CharField(blank=True,max_length=100)
    state = models.CharField(blank=True,max_length=100)
    country = models.CharField(blank=True,max_length=100)
