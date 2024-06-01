from django import forms
from .models import Order
from .models import Addresses
from .models import BillingAddress


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','order_note']



class AddressesForm(forms.ModelForm):
    class Meta:
        model = Addresses
        fields = ['first_name', 'last_name', 'email', 'phone', 'address_line_1', 'address_line_2', 'city', 'state', 'country']





class ReturnRequestForm(forms.Form):
    return_reason = forms.CharField(label='Reason for return', widget=forms.Textarea)
    # Add more fields as needed

class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ['first_name', 'last_name', 'email', 'phone', 'address_line_1', 'address_line_2', 'city', 'state', 'country']

class WalletDeductionForm(forms.Form):
    deduction_amount = forms.DecimalField(label='Deduction Amount', min_value=0.01, max_digits=10, decimal_places=2, required=True)



    