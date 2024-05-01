from django.shortcuts import render, get_object_or_404,redirect
from .models import PopularProduct,ProductGallery,ReviewRating
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
        in_wish = CartItem.objects.filter(cart__cart_id = _cart_id(request),product=single_product).exists()    # using this from cart item we access cart and using foreign key access cart id & _cart_id(request)  is the private function created to store session id.if this query has any object it returns exists().Then it shows true(product exist in cart) and does nt show any add to cart button
        
    except Exception as e:
        raise e
    
    #Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product' : single_product,
        'in_wish'    :  in_wish,
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
'''
def submit_review(request, product_id):
    # Get the product instance
    product = get_object_or_404(PopularProduct, id=product_id)

    if request.method == 'POST':
        # Create or update review
        try:
            review = ReviewRating.objects.get(user=request.user, product=product)
            form = ReviewForm(request.POST, instance=review)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)

        if form.is_valid():
            # Save the form data
            form.instance.user = request.user
            form.instance.product = product
            form.save()
            # Display success message
            if review:
                messages.success(request, 'Your review has been updated successfully.')
            else:
                messages.success(request, 'Your review has been submitted successfully.')
            return redirect(request.META.get('HTTP_REFERER'))  # Redirect back to the previous page after submission
        else:
            # Form is invalid, show error messages
            messages.error(request, 'Failed to submit review. Please check the form.')
            # Optionally, print form errors for debugging
            print(form.errors)
            return HttpResponseBadRequest("Invalid form data")

    # If request method is not POST, redirect to the product detail page
    return redirect(product.get_url())
'''

def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER') # THE REVIEWING PRODUCT URL STORED IN THIS url variable
    print("product url:",url)
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)   #user__id means user id TAKEN FROM foriegn key Accounts, simlarly product__id taken from popularproducta using foreign key
            form = ReviewForm(request.POST,instance=reviews)    # request.POST having all the data which we enter to rating & if already a review uploaded using instace we can update the review
            form.save()
            print("values of updated form",form)
            messages.success(request,'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            print("values of Reviewform",form)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')  #remote address store ip address
                data.product_id=product_id
                data.user_id = request.user.id
                data.save()
                print("values of data",data)
                messages.success(request,'Thank you! Your review has been submitted.')
                return redirect(url)
    return HttpResponse("Error: Invalid request") 
    
'''
def filter_and_sort_products(request):
    if request.method == 'GET':
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        # Filter products based on price range
        if min_price is not None and max_price is not None:
            products = PopularProduct.objects.filter(price__gte=min_price, price__lte=max_price)
        else:
            products = PopularProduct.objects.all()
        
        # Sort products by price
        sorted_products = products.order_by('price','-created_at')  # Change 'price' to '-price' for descending order
        
        context = {
            'products': sorted_products
        }
        return render(request, 'store/store.html', context)
'''

def filter_and_sort_products(request):
    if request.method == 'GET':
        sort_by = request.GET.get('sort_by_price')
        if sort_by == 'price':
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')
            # Filter products based on price range
            if min_price is not None and max_price is not None:
                products = PopularProduct.objects.filter(price__gte=min_price, price__lte=max_price)
            else:
                products = PopularProduct.objects.all()
            # Sort products by price
            sorted_products = products.order_by('price')  # Change 'price' to '-price' for descending order
        elif sort_by == 'newly_added':
            # Sort products by newly added
            sorted_products = PopularProduct.objects.all().order_by('-created_date')
        else:
            # Default sorting
            sorted_products = PopularProduct.objects.all()

        context = {
            'products': sorted_products
        }
        return render(request, 'store/store.html', context)