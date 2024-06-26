from django.contrib import admin
from .models import Payment,Order,OrderProduct,Addresses,Wallet,ReturnRequest
from django.db.models import Sum
from django.views import View
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import DateField, Count, Sum

from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from .models import Order, SalesReportNew
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from django.core.paginator import Paginator
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle







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

class SalesReportAdmin(admin.ModelAdmin):
    change_list_template = "admin/sales_report.html"

    def changelist_view(self, request, extra_context=None):
        # Default start and end dates for custom date range
        start_date = end_date = None

        # Default date range selection
        date_range = request.GET.get('date_range', 'custom')

        # Get today's date
        today = timezone.now().date()

        # Set start and end dates based on date range selection
        if date_range == 'daily':
            start_date = end_date = today
        elif date_range == 'weekly':
            start_date = today - timezone.timedelta(days=today.weekday())
            end_date = start_date + timezone.timedelta(days=6)
        elif date_range == 'monthly':
            start_date = today.replace(day=1)
            next_month = today.replace(day=28) + timezone.timedelta(days=4)  # this will never fail
            end_date = next_month - timezone.timedelta(days=next_month.day)
        elif date_range == 'yearly':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            start_date = today.replace(day=1)
            end_date = today

        # Get orders within the selected date range
        orders = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).order_by('-created_at')

        # Calculate total sales amount
        total_sales_amount = round(orders.aggregate(total_sales=Sum('order_total'))['total_sales'] or 0, 2)

        # Calculate total discount
        total_discount = orders.aggregate(total_discount=Sum('discount'))['total_discount'] or 0

        # Calculate total coupon count
        total_coupon_count = orders.exclude(coupon=None).count()

        # Calculate overall sales count
        overall_sales_count = orders.count()

        # Check if SalesReport instance already exists for the specified date range
        sales_report_instance, created = SalesReportNew.objects.get_or_create(
            start_date=start_date,
            end_date=end_date,
            date_range=date_range,
            defaults={
                'overall_sales_count': overall_sales_count,
                'total_sales_amount': total_sales_amount,
                'total_discount': total_discount,
                'total_coupon_count': total_coupon_count
            }
        )
        if not created:
            sales_report_instance.overall_sales_count = overall_sales_count
            sales_report_instance.total_sales_amount = total_sales_amount
            sales_report_instance.total_discount = total_discount
            sales_report_instance.total_coupon_count = total_coupon_count
            sales_report_instance.save()

        # Add pagination
        paginator = Paginator(orders, 10)  # Show 10 orders per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'orders': orders,
            'sales_report_instance': sales_report_instance,
            'total_sales_amount': total_sales_amount,
            'total_discount': total_discount,
            'total_coupon_count': total_coupon_count,
            'overall_sales_count': overall_sales_count,
            'start_date': start_date,
            'end_date': end_date,
            'date_range': date_range,
            'page_obj': page_obj,
        }

        return render(request, "admin/sales_report.html", context)
    
    def generate_sales_report_pdf(self, request):
        # Fetch the sales report data using the same logic as in the changelist_view
        date_range = request.GET.get('date_range', 'custom')
        today = timezone.now().date()

        if date_range == 'daily':
            start_date = end_date = today
        elif date_range == 'weekly':
            start_date = today - timezone.timedelta(days=today.weekday())
            end_date = start_date + timezone.timedelta(days=6)
        elif date_range == 'monthly':
            start_date = today.replace(day=1)
            next_month = today.replace(day=28) + timezone.timedelta(days=4)  # this will never fail
            end_date = next_month - timezone.timedelta(days=next_month.day)
        elif date_range == 'yearly':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            start_date = today.replace(day=1)
            end_date = today

        orders = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).order_by('-created_at')
        total_sales_amount = round(orders.aggregate(total_sales=Sum('order_total'))['total_sales'] or 0, 2)
        total_discount = orders.aggregate(total_discount=Sum('discount'))['total_discount'] or 0
        total_coupon_count = orders.exclude(coupon=None).count()
        overall_sales_count = orders.count()

        # Create the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        centered_style = styles['Title']
        centered_style.alignment = 1  # Center alignment

        # Add sales report content in the middle of the first page
        elements.append(Paragraph("Sales Report", centered_style))
        elements.append(Spacer(1, 40))

        elements.append(Paragraph(f"Date Range: {start_date} to {end_date}", styles['Normal']))
        elements.append(Paragraph(f"Total Sales Amount: ${total_sales_amount}", styles['Normal']))
        elements.append(Paragraph(f"Total Discount: ${total_discount}", styles['Normal']))
        elements.append(Paragraph(f"Total Coupon Count: {total_coupon_count}", styles['Normal']))
        elements.append(Paragraph(f"Overall Sales Count: {overall_sales_count}", styles['Normal']))
        elements.append(Spacer(1, 50))

        # Prepare table data
        data = [['S.No', 'Date', 'Order Number', 'Customer Name', 'Order Total']]
        for idx, order in enumerate(orders, start=1):
            data.append([
                idx,
                order.created_at.strftime("%Y-%m-%d"),
                order.order_number,
                f"{order.first_name} {order.last_name}",
                f"${order.order_total}",
            ])

        # Create a table and style it
        table = Table(data, colWidths=[0.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)

        # Build the PDF document
        doc.build(elements)

        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate_sales_report_pdf/', self.generate_sales_report_pdf, name='generate_sales_report_pdf'),
        ]
        return custom_urls + urls

admin.site.register(SalesReportNew, SalesReportAdmin)
admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Addresses)
admin.site.register(Wallet,WalletAdmin)

admin.site.register(ReturnRequest,ReturnRequestAdmin)



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


