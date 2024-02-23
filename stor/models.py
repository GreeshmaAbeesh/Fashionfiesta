from django.db import models
from category.models import Category

# Create your models here.
class Product(models.Model):
    product_name= models.CharField(max_length=255,unique=True)
    slug        = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price       = models.IntegerField()
    
    stock       = models.IntegerField()
    is_available= models.BooleanField(default=True)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date= models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product_name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/products/',blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.product_name}"