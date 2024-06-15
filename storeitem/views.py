from django.shortcuts import render, get_object_or_404,redirect
from .models import PopularProduct,ProductGallery,ReviewRating,Variation
from category.models import Category
import os
from cart.views import _cart_id
from cart.models import Cart,CartItem
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.http import HttpResponse,HttpResponseBadRequest
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages

# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = PopularProduct.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        page_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = PopularProduct.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        page_products = paginator.get_page(page)
        product_count = products.count()

    # Iterate through the products and get the active offer for each
    for product in page_products:
        product.offer = product.productoffer_set.filter(is_active=True).first()

    context = {
        'products': page_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)




def product_detail(request, category_slug, product_slug):
    try:
        single_product = PopularProduct.objects.get(category__slug=category_slug, slug=product_slug)
        in_wish = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

        # Get the active offer for the product, if any
        product_offer = single_product.productoffer_set.filter(is_active=True).first()
       
        

        # Get color variations and their images for the product
        color_variations = Variation.objects.filter(product=single_product, variation_category='color', is_active=True).exclude(variation_image='')
        color_images = {variation.variation_value.lower(): variation.variation_image.url for variation in color_variations if variation.variation_image}
        print('color_variations, color_images', color_variations, color_images)

        context = {
            'single_product': single_product,
            'in_wish': in_wish,
            'product_gallery': product_gallery,
            'product_offer': product_offer,  # Include the product offer in the context
            'color_images': color_images,  # Pass color variation images to the template
        }

        return render(request, 'store/product_detail.html', context)
    except Exception as e:
        raise e



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


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')  # The referring URL
    print("product url:", url)
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)  # Update existing review
            if form.is_valid():
                form.save()
                print("values of updated form", form)
                messages.success(request, 'Thank you! Your review has been updated.')
                return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            print("values of ReviewForm", form)
            if form.is_valid():
                data = form.save(commit=False)
                data.ip = request.META.get('REMOTE_ADDR')  # Store IP address
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                print("values of data", data)
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
    return HttpResponse("Error: Invalid request")
    



def filter_and_sort_products(request):
    if request.method == 'GET':
        sort_by = request.GET.get('sort_by')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        # Start with all products
        products = PopularProduct.objects.all()

        # Filter products based on price range
        if min_price and max_price:
            products = products.filter(price__gte=min_price, price__lte=max_price)

        # Sort products
    if sort_by:
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'newly_added':
            products = products.order_by('-created_date')
        elif sort_by == 'name':
            products = products.order_by('product_name')
        
        context = {
            'products': products
        }
        return render(request, 'store/store.html', context)
