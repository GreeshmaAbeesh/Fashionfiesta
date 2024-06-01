from django.db import models
from category.models import Category
from django.urls import reverse
from accounts .models import Account
from django.utils import timezone

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
        return reverse('product_detail',args=[self.category.slug,self.slug]) # here product detail means name of the path and pass two arguments in list . ie category slug and product slug. self means popularproduct.self.category.slud means , category in self model and usind forign key it access category slug. self.slug means product slug


    def __str__(self):
        return self.product_name
    
    def get_offer(self):
        current_date = timezone.now()
        active_offers = self.productoffer_set.filter(is_active=True, start_date__lte=current_date, end_date__gte=current_date)
        if active_offers.exists():
            return active_offers.first()
        return None

    def get_price_after_offer(self):
        offer = self.get_offer()
        if offer:
            discount_amount = self.price * (offer.discount_percentage / 100)
            return self.price - discount_amount
        return self.price


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active = True)
    
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active = True)


#These choices are used to create a dropdown menu or radio button options when interacting with the field in forms or the Django admin interface.

variation_category_choice = (
    ('color','color'),   #This is a tuple representing one choice. The first element ('color') is the value stored in the database, and the second element ('color') is a human-readable description or label.
    ('size','size'),
)


class Variation(models.Model):
    product = models.ForeignKey(PopularProduct, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    variation_image = models.ImageField(upload_to='variation_images/', null=True, blank=True)  # New field for variation image
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)


    objects = VariationManager()

    def __str__(self):
        return self.variation_value



class ProductGallery(models.Model):
    product = models.ForeignKey(PopularProduct,default=None,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products',max_length=255)


    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'


class ProductOffer(models.Model):
    product = models.ForeignKey(PopularProduct, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.discount_percentage}% off"

    def is_valid(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    

class ReviewRating(models.Model):
    product = models.ForeignKey(PopularProduct,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,blank=True)
    review = models.TextField(max_length=500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.subject