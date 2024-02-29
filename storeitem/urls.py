from django.urls import path
from .import views
#from .views import product_detail
from cart.views import add_cart

urlpatterns = [
    
    path('',views.store,name='store'),
    path('<slug:category_slug>/',views.store,name='products_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/',views.product_detail,name='product_detail'),
    path('add_cart/<int:product_id>/', add_cart, name='add_cart'), 
]
   
