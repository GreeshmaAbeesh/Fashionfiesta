from django.contrib import admin
from .models import Payment,Order,OrderProduct,Addresses,Wallet,ReturnRequest,SalesReportNew
from django.db.models import Sum
from django.views import View
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import DateField, Count, Sum



#from .views import sales_report  # Import your existing sales_report view
#from django.views.generic import TemplateView
#from django.urls import path

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('payment','user','product','quantity','product_price','ordered')


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','phone','email','city','order_total','tax','status','is_ordered','created_at']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name','phone','email']
    list_per_page = 20
    inlines = [OrderProductInline]


class WalletAdmin(admin.ModelAdmin):
    list_display = ('user','balance')


class CouponAdmin(admin.ModelAdmin):
    list_display = ('user','discount')

class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order','return_reason')


# class SalesReportAdmin(admin.ModelAdmin):
#     list_display = ('order_date', 'total_amount', 'discount', 'coupon_deduction', 'coupon_count', 'coupon_total', 'user')
#     list_filter = ('order_date', 'user')
#     search_fields = ['order_date', 'user__username']

#     def coupon_count(self, obj):
#         return obj.order.coupon_count

#     def coupon_total(self, obj):
#         return obj.order.coupon_total
'''
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('order_date', 'total_amount', 'discount', 'coupon_deduction', 'get_coupon_count', 'get_coupon_total', 'user')
    list_filter = ('order_date', 'user')
    search_fields = ['order_date', 'user__username']

    def get_coupon_count(self, obj):
        # Calculate coupon count from related orders
        return obj.order.aggregate(total_coupon_count=Sum('coupon_count'))['total_coupon_count'] or 0
    get_coupon_count.short_description = 'Coupon Count'

    def get_coupon_total(self, obj):
        # Calculate total coupon amount from related orders
        return obj.order.aggregate(total_coupon_total=Sum('coupon_total'))['total_coupon_total'] or 0
    get_coupon_total.short_description = 'Coupon Total'

class SalesReportAdminView(View):
    def get(self, request):
        # Call your existing sales_report view and return its response
        return sales_report(request)

#admin.site.register_view('sales_report', 'Sales Report', view=SalesReportAdminView.as_view())
'''

class SalesReportNewAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date', 'date_range', 'overall_sales_count', 'total_sales_amount', 'total_discount']
    




admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Addresses)
admin.site.register(Wallet,WalletAdmin)

admin.site.register(ReturnRequest,ReturnRequestAdmin)
admin.site.register(SalesReportNew,SalesReportNewAdmin)


# Add a custom admin page for sales report# Add a custom admin page for sales report
#class SalesReportAdminView(TemplateView):
 #   template_name = 'admin/sales_report.html'

# # Register the custom admin view with a custom URL
# class MyAdminSite(admin.AdminSite):
#     def get_urls(self):
#         urls = super().get_urls()
#         my_urls = [
#             path('sales_report/', self.admin_view(SalesReportAdminView.as_view()), name='sales_report'),
#         ]
#         return my_urls + urls

# # Replace the default admin site with your custom admin site
# admin.site = MyAdminSite()


