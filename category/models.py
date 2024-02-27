from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.SlugField(max_length=100,unique=True)
    description=models.TextField(blank=True)
    cat_image=models.ImageField(upload_to='photos/categories',blank=True)

    class Meta:
        verbose_name='category'
        verbose_name_plural='categories'

    def get_url(self):
        return reverse('products_by_category',args=[self.slug]) # use reverse fn reverse is a Django utility function that is used to generate a URL for a given view name and its arguments., use name of the slug in the urls of storeitem[here this function bring the url of the perticular category]

    def __str__(self):
        return self.category_name