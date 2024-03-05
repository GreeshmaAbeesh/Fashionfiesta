from django.shortcuts import render
from storeitem.models import PopularProduct

def home(request):
    products = PopularProduct.objects.all().filter(is_available=True)

    context = {
        'products' : products,
    }
    return render(request,'home.html',context)


