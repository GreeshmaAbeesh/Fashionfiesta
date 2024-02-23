from django.shortcuts import render
from stor.models import Product,ProductImage

def home(request):
    products = Product.objects.all().filter(is_available=True)
    product_images = ProductImage.objects.filter(product__in=products)

    context = {
        'products' : zip(products,product_images)
    }
    return render(request,'home.html',context)
