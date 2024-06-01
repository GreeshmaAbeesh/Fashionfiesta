from django import forms



class BillingAddressForm(forms.ModelForm):
    class Meta:
        
        fields = ['first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','order_note']


class CouponApplyForm(forms.Form):
    code = forms.CharField()