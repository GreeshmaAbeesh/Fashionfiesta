from django.urls import path
from .import views
#from .views import SalesReportAdminView

urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('order_complete/',views.order_complete,name='order_complete'),
    path('cash_on_delivery/',views.cash_on_delivery,name='cash_on_delivery'),
    path('save_address/', views.save_address, name='save_address'),
    #path('address_list/', views.address_list, name='address_list'),
    path('coupon/',views.coupon,name='coupon'),
    path('coupon_activate/', views.coupon_activate, name='coupon_activate'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('return_request/<int:order_id>/', views.return_request, name='return_request'),
    path('wallet/', views.wallet, name='wallet'),
    #path('save_billing_address/', views.save_billing_address, name='save_billing_address'),
    path('sales_report/', views.sales_report, name='sales_report'),
    #path('sales_report/', SalesReportAdminView.as_view(), name='sales_report'),
    #path('order_complete_pdf/',views.order_complete_pdf,name='order_complete_pdf'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    
]
   
