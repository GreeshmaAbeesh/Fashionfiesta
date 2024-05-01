from django.shortcuts import render,redirect,get_object_or_404
from storeitem.models import PopularProduct,Variation,ProductGallery
from .models import Wishlist,WishlistItem
from cart.models import Cart
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F
# Create your views here.


def _wishlist_id(request):                  # cart made as private
    wishlist = request.session.session_key  # inside cookies there is session and it gives session id.
    if not wishlist:                        # if there is no asession, it will create new session
        wishlist = request.session.create()
    return wishlist                        # here return the cart id

# we get the product here

def add_wishlist(request,product_id):
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
                print('inside add wishlist',variation)
                product_variation.append(variation)  # here insert values to a cart item
            except:
                pass
        
   
    #we get wishlist
    try:
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request)) #here  it will match cart id with session id. get the cart using the cart_id. [ we need to cart id from session.ie inside cookies there is session and it gives session id.. that session is taken as cart id]
    except Wishlist.DoesNotExist:
        wishlist = Wishlist.objects.create(
            wishlist_id =_wishlist_id(request)
        )
    wishlist.save()

    #we get wishlistitem
    print("above is wishlistitem exist")
    print('wishlist,user,product',wishlist,request.user,product)
    is_wishlist_item_exists = WishlistItem.objects.filter(product=product,wishlist=wishlist,user=request.user).exists()
    if is_wishlist_item_exists:
        print("inside is wishlistitem exist")
        wishlist_item = WishlistItem.objects.filter(product=product,wishlist=wishlist,user=request.user)      # return cart item objects
        #existing variations from database
        #current variations in product_variation list
        # item_id from database
        ex_var_list = []
        id = []
        for item in wishlist_item:    #check weather the current variation inside exsting variation then increase quantity of item
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        print(ex_var_list)

        if product_variation in ex_var_list:
            # increase the cart item quantity
            index =  ex_var_list.index(product_variation)
            item_id = id[index]
            item = WishlistItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        
        else:
            #create new cart item
            item = WishlistItem.objects.create(product=product, quantity=1, wishlist=wishlist,user=request.user)
            if len(product_variation)>0:   #if product variation list not empty
                item.variations.clear()
                item.variations.add(*product_variation) 
            item.save()

    else:
        wishlist_item = WishlistItem.objects.create(
            product = product,
            quantity = 1,      # 1 because it is new cartitem
            wishlist  = wishlist,
            user = request.user,
        )
        if len(product_variation)>0:   #if product variation in empty list
            wishlist_item.variations.clear()
            wishlist_item.variations.add(*product_variation)
        wishlist_item.save()

    

    return redirect('wishlist')

'''
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    # Your code to render the cart items goes here 
    print('cart_items:',cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items})
'''

def remove_wishlist(request, product_id,wishlist_item_id):                        # this function is used to reduce cart item while clicking minus button
    wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
    product = get_object_or_404(PopularProduct,id=product_id)
    try:
        wishlist_item = WishlistItem.objects.get(product=product , wishlist=wishlist, id=wishlist_item_id)
        if wishlist_item.quantity > 1:
            wishlist_item.quantity -= 1
            wishlist_item.save()
        else:
            wishlist_item.delete()
    except:
        pass
    return redirect('wishlist')



def remove_wishlist_item(request, product_id,wishlist_item_id):
    wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
    product = get_object_or_404(PopularProduct,id=product_id)        
    wishlist_item = WishlistItem.objects.get(product=product , wishlist=wishlist,id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')



        
    
def wishlist(request, total=0, quantity=0, wishlist_items=None):           # to modify cart function and add items to cart
    try:
        tax = 0
        grand_total = 0
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist,is_active=True).order_by(F('product__price').asc()) 
        for wishlist_item in wishlist_items:
            total += (wishlist_item.product.price * wishlist_item.quantity)
            quantity += wishlist_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass 

    context = {
        'total' : total,
        'quantity' : quantity,
        'wishlist_items' : wishlist_items,
        'tax' : tax ,
        'grand_total' : grand_total,
    }
    return render(request,'store/wishlist.html',context)   



'''
@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass 

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax ,
        'grand_total' : grand_total,
    }
    return render(request,'store/checkout.html',context)
'''
