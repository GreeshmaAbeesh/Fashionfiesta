from django.db import models
from storeitem .models import PopularProduct,Variation

# Create your models here.

class Cart(models.Model):
    cart_id    = models.CharField(max_length=250,blank=True)
    date_added = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.cart_id
    

class CartItem(models.Model):
    product = models.ForeignKey(PopularProduct, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart    = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity  #here self.product.price means inside CartItem-product-price in PopularProduct using foreign key  * quantity od item in  CartItem-

    def __unicode__(self):
        return self.product