from django.shortcuts import render,redirect,get_object_or_404
from storeitem.models import PopularProduct,Variation,ProductOffer
from orders.models import Wallet,OrderProduct,Order,Addresses
from category.models import Category
from .models import Cart,CartItem,Coupon
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models import Count
from .forms import CouponApplyForm
from django.utils import timezone
#from .models import ProductOffer
# Create your views here.


def _cart_id(request):                  # cart made as private
    cart = request.session.session_key  # inside cookies there is session and it gives session id.
    if not cart:                        # if there is no asession, it will create new session
        cart = request.session.create()
    return cart                         # here return the cart id

# we get the product here

def add_cart(request,product_id):
    product=PopularProduct.objects.get(id=product_id)  # to get the product
    # we get product variation here
    product_variation = []          # inside this list we have color and size
    if request.method == 'POST':
        #quantity = int(request.POST.get('quantity',1))
        for item in request.POST:
            key = item            # if color is black,color will stored in the key
            value = request.POST[key]   # black is stored in the value
            
            #to check the match of variation category in model and value

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                print('inside add cart',variation)
                product_variation.append(variation)  # here insert values to a cart item
            except:
                pass
        
   
    #we get cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) #here  it will match cart id with session id. get the cart using the cart_id. [ we need to cart id from session.ie inside cookies there is session and it gives session id.. that session is taken as cart id]
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id =_cart_id(request)
        )
    cart.save()

    #we get cartitem
    print("above is cartitem exist")
    print('cart,user,product',cart,request.user,product)
    is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart,user=request.user).exists()
    if is_cart_item_exists:
        print("inside is cartitem exist")
        cart_item = CartItem.objects.filter(product=product,cart=cart,user=request.user)      # return cart item objects
        #existing variations from database
        #current variations in product_variation list
        # item_id from database
        ex_var_list = []
        id = []
        for item in cart_item:    #check weather the current variation inside exsting variation then increase quantity of item
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        print(ex_var_list)

        if product_variation in ex_var_list:
            # increase the cart item quantity
            index =  ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        
        else:
            #create new cart item
            item = CartItem.objects.create(product=product, quantity=1, cart=cart,user=request.user)
            if len(product_variation)>0:   #if product variation list not empty
                item.variations.clear()
                item.variations.add(*product_variation) 
            item.save()

    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,      # 1 because it is new cartitem
            cart  = cart,
            user = request.user,
        )
        if len(product_variation)>0:   #if product variation in empty list
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect('cart')



def remove_cart(request, product_id,cart_item_id):                        # this function is used to reduce cart item while clicking minus button
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(PopularProduct,id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product , cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')



def remove_cart_item(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(PopularProduct,id=product_id)        
    cart_item = CartItem.objects.get(product=product , cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

        
    
def cart(request, total=0, quantity=0, cart_items=None):           # to modify cart function and add items to cart
    try:
        tax = 0
        grand_total = 0
        discount = 0  # Initialize discount here
        coupon = None  # Initialize coupon here
        original_total = 0  # Initialize original_total
        offer = 0  # Initialize offer here
        savings = 0

        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True).order_by(F('product__price').asc()) 
        
         # Check if there is an active coupon in the session
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
            except Coupon.DoesNotExist:
                coupon = None

        

        for cart_item in cart_items:
           
            product = cart_item.product
            offer = ProductOffer.objects.filter(product=product, start_date__lte=timezone.now(), end_date__gte=timezone.now()).first()
            
            if offer:
                cart_item.original_price = product.price  # Save the original price
                total += (product.price * (1 - (offer.discount_percentage / 100)) * cart_item.quantity)
                product.price = product.price - (product.price * (offer.discount_percentage / 100))
                original_total += cart_item.original_price * cart_item.quantity  # Add to original total
            else:
                total += (product.price * cart_item.quantity)
                cart_item.original_price = product.price  # Save the original price
                original_total += cart_item.original_price * cart_item.quantity  # Add to original total
                #total += (cart_item.product.price * cart_item.quantity)
            cart_item.original_price = cart_item.original_price * cart_item.quantity
            quantity += cart_item.quantity
            

        if coupon:
            discount = (coupon.discount / 100) * total
            total -= discount


        tax = (2 * total)/100
        grand_total = total + tax
        savings = original_total - grand_total  # Calculate the total savings


        
    except ObjectDoesNotExist:
        pass 

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax ,
        'grand_total' : grand_total,
        'coupon': coupon,
        'discount': discount,
        'offer_id': offer,
        'savings': savings, 
        
    }

    
    return render(request,'store/cart.html',context)   




@login_required(login_url='login')
def checkout(request,total=0, quantity=0, cart_items=None):
   # wallet = Wallet.objects.get(id=wallet_id)
    try:
        tax = 0
        grand_total = 0
        discount = 0  # Initialize discount here
        coupon = None  # Initialize coupon here
        original_total = 0  # Initialize original_total

        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)

         # Check if there is an active coupon in the session
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
            except Coupon.DoesNotExist:
                coupon = None


        for cart_item in cart_items:
            # Apply product offer if available
            product = cart_item.product
            offer = ProductOffer.objects.filter(product=product, start_date__lte=timezone.now(), end_date__gte=timezone.now()).first()
            if offer:
                cart_item.original_price = product.price  # Save the original price
                total += (product.price * (1 - (offer.discount_percentage / 100)) * cart_item.quantity)
                product.price = product.price - (product.price * (offer.discount_percentage / 100))
                original_total += cart_item.original_price * cart_item.quantity  # Add to original total
            else:
                total += (product.price * cart_item.quantity)
                cart_item.original_price = product.price  # Save the original price
                original_total += cart_item.original_price * cart_item.quantity  # Add to original total
                #total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        if coupon:
            discount = (coupon.discount / 100) * total
            total -= discount


        tax = (2 * total)/100
        grand_total = total + tax
        savings = original_total - grand_total  # Calculate the total savings

        # Fetch saved addresses for the current user
        addresses = Addresses.objects.filter(user=request.user)        
    except ObjectDoesNotExist:
        pass 

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax ,
        'grand_total' : grand_total,
        #'wallet' : wallet,
        'coupon': coupon,
        'discount': discount,
        'savings': savings, 
        'addresses' : addresses,
    }
    return render(request,'store/checkout.html',context)


def apply_coupon(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST or None)
    
    if form.is_valid():
        code = form.cleaned_data['code']
       
        
        # Check if the coupon exists
        coupon = Coupon.objects.filter(code=code, active=True, valid_from__lte=now, valid_to__gte=now).first()
        print('coupon is',coupon)

        if coupon:
            try:
                coupon = Coupon.objects.get(code=code, active=True, valid_from__lte=now, valid_to__gte=now)
                print('coupon from adminside',coupon)
                print('coupon.id',coupon.id)
                request.session['coupon_id'] = coupon.id

                # Update user's orders with the applied coupon
                orders = Order.objects.filter(user=request.user, coupon=None)
                for order in orders:
                    order.coupon = coupon
                    order.save()

                # Increment the usage count
                coupon.usage_count += 1
                coupon.save()
                
                return redirect('cart')
            except Coupon.DoesNotExist:
                form.add_error('code', 'This coupon does not exist or is not valid.')
    
    if request.method == 'POST' and 'remove_coupon' in request.POST:
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        return redirect('cart')
    return render(request, 'apply_coupon.html', {'form': form})



def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    return redirect('cart')