from django import forms
from .models import Order
from .models import Addresses
from .models import Coupon


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','order_note']



class AddressesForm(forms.ModelForm):
    class Meta:
        model = Addresses
        fields = ['first_name', 'last_name', 'email', 'phone', 'address_line_1', 'address_line_2', 'city', 'state', 'country']


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['first_name', 'last_name', 'email', 'phone', 'address_line_1', 'address_line_2', 'city', 'state', 'country','discount','code','active','order']