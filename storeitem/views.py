from django.shortcuts import render, get_object_or_404
from storeitem.models import PopularProduct
from category.models import Category
import os
from cart.views import _cart_id
from cart.models import Cart,CartItem

# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)   # if category found, it bring objects otherwise return 404 error(inside it pass category model name & slug inside that model)
        products  = PopularProduct.objects.filter(category=categories,is_available=True)
        product_count = products.count()
    else:
        products = PopularProduct.objects.all().filter(is_available=True)
        product_count = products.count()

    context = {
        'products' : products,
        'product_count' : product_count,
    }
    return render(request, 'store/store.html',context)



def product_detail(request,category_slug,product_slug):
    try:
        single_product = PopularProduct.objects.get(category__slug=category_slug,slug=product_slug)  # __ is the syntax for accessing slug of category.ie from PopularProduct model we get category, iside the category app we have category we have slug model .to access that we using category__slug
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product=single_product).exists()    # using this from cart item we access cart and using foreign key access cart id & _cart_id(request)  is the private function created to store session id.if this query has any object it returns exists().Then it shows true(product exist in cart) and does nt show any add to cart button
        
    except Exception as e:
        raise e
    context = {
        'single_product' : single_product,
        'in_cart'    :  in_cart,
    }
    return render(request, 'store/product_detail.html',context)
    