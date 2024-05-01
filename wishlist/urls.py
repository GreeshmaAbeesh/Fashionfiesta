from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns...
    path('', views.wishlist,name='wishlist'),
    path('add_wishlist/ <int:product_id>/',views.add_wishlist,name='add_wishlist'),
    path('remove_wishlist/<int:product_id>/<int:wishlist_item_id>/',views.remove_wishlist,name='remove_wishlist'),
    path('remove_wishlist_item/ <int:product_id>/<int:wishlist_item_id>/',views.remove_wishlist_item,name='remove_wishlist_item'),
]