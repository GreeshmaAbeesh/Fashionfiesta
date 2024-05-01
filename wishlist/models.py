from django.db import models
from storeitem .models import PopularProduct,Variation
from accounts .models import Account


# Create your models here.

class Wishlist(models.Model):
    wishlist_id    = models.CharField(max_length=250,blank=True)
    date_added = models.DateField(auto_now_add=True)
   

    def __str__(self):
        return self.wishlist_id
    

class WishlistItem(models.Model):
   
    user = models.ForeignKey(Account, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(PopularProduct, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    wishlist    = models.ForeignKey(Wishlist, on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity  #here self.product.price means inside CartItem-product-price in PopularProduct using foreign key  * quantity od item in  CartItem-

    def __unicode__(self):
        return self.product