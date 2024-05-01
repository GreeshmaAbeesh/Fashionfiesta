from django.urls import path
from .import views
#from .views import product_detail
from cart.views import add_cart

urlpatterns = [
    
    path('',views.store,name='store'),
    path('category/<slug:category_slug>/',views.store,name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detail,name='product_detail'),
    
    path('add_cart/<int:product_id>/', add_cart, name='add_cart'), 
    path('search/',views.search,name='search'),
    path('submit_review/<int:product_id>',views.submit_review,name='submit_review'),
    path('filter_and_sort_products/',views.filter_and_sort_products,name='filter_and_sort_products'),
]
   
