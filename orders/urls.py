from django.urls import path
from .import views
from django.contrib import admin
from .admin import SalesReportAdmin

urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('order_complete/',views.order_complete,name='order_complete'),
    path('cash_on_delivery/',views.cash_on_delivery,name='cash_on_delivery'),
    path('save_address/', views.save_address, name='save_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('edit_address/<int:address_id>/',views.edit_address, name='edit_address'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('return_request/<int:order_id>/', views.return_request, name='return_request'),
    path('wallet/', views.wallet, name='wallet'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('admin/sales-report/', SalesReportAdmin.changelist_view, name='sales_report'),
]
   
