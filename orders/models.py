from django.db import models
from accounts.models import Account
from storeitem.models import PopularProduct,Variation
from cart.models import Coupon
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid
from django.utils import timezone

# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.payment_id
    

class Order(models.Model):
    STATUS = (
        ('Cash_on_delivery','Cash_on_delivery'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Returned','Returned'),
        ('Not_Completed','Not_Completed'),

    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    payment_id = models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL)
    
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50,choices=STATUS, default='New')
    ip = models.CharField(max_length=20, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self):
        return self.first_name



class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL,blank=True,null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(PopularProduct, on_delete=models.CASCADE)
    #variation = models.ForeignKey(Variation, on_delete=models.CASCADE,blank=True,null=True)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)


    def __str__(self):
        return self.product.product_name
    
class BillingAddress(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address_line_1= models.CharField(max_length=255)
    address_line_2= models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self):
        return self.full_name



class Addresses(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    order_note = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.first_name},{self.last_name},{self.address_line_1}, {self.city}, {self.country}"





    
    



class Wallet(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.first_name
    


class ReturnRequest(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    return_reason = models.TextField()
    is_returned = models.BooleanField(default=False)  # Add this field

'''
class SalesReport(models.Model):
    order_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon_deduction = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(Account, on_delete=models.CASCADE) # Assuming each sales report is associated with a user
    
    def __str__(self):
        return f"Sales Report - {self.order_date}"

    @classmethod
    def generate_sales_report(cls, start_date, end_date):
        # This method can be used to generate a sales report for a custom date range
        sales_reports = cls.objects.filter(order_date__range=[start_date, end_date])
        return sales_reports

    @classmethod
    def overall_sales_count(cls):
        # This method calculates the overall sales count
        return cls.objects.count()

    @classmethod
    def overall_order_amount(cls):
        # This method calculates the overall order amount
        return cls.objects.aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0

    @classmethod
    def overall_discount(cls):
        # This method calculates the overall discount
        return cls.objects.aggregate(models.Sum('discount'))['discount__sum'] or 0

'''



class SalesReportNew(models.Model):

    
    overall_sales_count = models.BigIntegerField(default=0)
    total_sales_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_coupon_count = models.BigIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    date_range = models.CharField(max_length=50)
    



    def __str__(self):
        return f"Sales Report from {self.start_date} to {self.end_date}"







