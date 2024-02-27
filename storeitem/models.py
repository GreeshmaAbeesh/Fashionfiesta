from django.db import models
from category.models import Category
from django.urls import reverse

# Create your models here.
class PopularProduct(models.Model):
    product_name= models.CharField(max_length=255,unique=True)
    slug        = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price       = models.IntegerField()
    images      = models.ImageField(upload_to='photos/products')
    stock       = models.IntegerField()
    is_available= models.BooleanField(default=True)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date= models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)

#this is used to make the product_details link working while clicking on the product name. 
    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug]) # here product detail means name of the path and pass two argumenta in list . ie category slug and product slug. self means popularproduct.self.category.slud means , category in self model and usind forign key it access category slug. self.slug means product slug


    def __str__(self):
        return self.product_name
    