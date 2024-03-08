from django.shortcuts import render, get_object_or_404
from storeitem.models import PopularProduct,ProductGallery
from category.models import Category
import os
from cart.views import _cart_id
from cart.models import Cart,CartItem
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)   # if category found, it bring objects otherwise return 404 error(inside it pass category model name & slug inside that model)
        products  = PopularProduct.objects.filter(category=categories,is_available=True)
        paginator = Paginator(products,3)      # from category wise product, 3 products stored in paginator
        page = request.GET.get('page')    # this step is to get the page which we want
        page_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = PopularProduct.objects.all().filter(is_available=True).order_by('id') # here we get full products in the order of id
        paginator = Paginator(products,6)      # from all products 6 products stored in paginator
        page = request.GET.get('page')    # this step is to get the page which we want
        page_products = paginator.get_page(page)  #6 products in paginator stored in page_products.. and this page_products passed inside the template
        product_count = products.count()

    context = {
        'products' : page_products,
        'product_count' : product_count,
    }
    return render(request, 'store/store.html',context)



def product_detail(request,category_slug,product_slug):
    try:
        single_product = PopularProduct.objects.get(category__slug=category_slug,slug=product_slug)  # __ is the syntax for accessing slug of category.ie from PopularProduct model we get category, iside the category app we have category we have slug model .to access that we using category__slug
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product=single_product).exists()    # using this from cart item we access cart and using foreign key access cart id & _cart_id(request)  is the private function created to store session id.if this query has any object it returns exists().Then it shows true(product exist in cart) and does nt show any add to cart button
        
    except Exception as e:
        raise e
    
    #Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product' : single_product,
        'in_cart'    :  in_cart,
        'product_gallery' : product_gallery,
    }
    return render(request,'store/product_detail.html',context)




def search(request):
    if 'keyword' in request.GET:    # in template name of key in search bar is given as keyword
        keyword = request.GET['keyword']    # here first check the get reques that keyword, if that keyword is present ,take its value and store it in the keyword variable
        # check the given keyword is blank or not
        if keyword:
            products = PopularProduct.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)) #-created_date means descending order. ie new product will come first.
            product_count = products.count()    # it gives number of items we got after search 
    context = {
        'products' : products,
        'product_count' :  product_count,
    }
    return render(request, 'store/store.html',context)