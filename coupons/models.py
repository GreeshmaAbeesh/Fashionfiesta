from django.db import models
from orders.models import Order
from django.core.validators import MinValueValidator

# Create your models here.
class Coupon(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True,blank=True, related_name='coupons')
    code = models.CharField(max_length=50,unique=True)
    discount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    #@classmethod
    #def activate_default_coupon(cls):
    #    default_code = "CODE1234"
    #    default_coupon, created = cls.objects.get_or_create(
    #        code=default_code,
    #        defaults={'discount': 20.00}  # Set your default discount here
    #    )
    #    if created:
    #       default_coupon.active = True
    #        default_coupon.save()
