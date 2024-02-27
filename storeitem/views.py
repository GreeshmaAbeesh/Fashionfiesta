from django.shortcuts import render, get_object_or_404
from storeitem.models import PopularProduct
from category.models import Category
import os


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
    except Exception as e:
        raise e
    context = {
        'single_product' : single_product,
    }
    return render(request, 'store/product_detail.html',context)
    