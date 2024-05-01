from django.urls import path
from .import views

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
    
]
   
