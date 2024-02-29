from django.shortcuts import render,redirect,get_object_or_404
from storeitem.models import PopularProduct
from .models import Cart,CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


def _cart_id(request):                  # cart made as private
    cart = request.session.session_key  # inside cookies there is session and it gives session id.
    if not cart:                        # if there is no asession, it will create new session
        cart = request.session.create()
    return cart                         # here return the cart id

def add_cart(request,product_id):
    product=PopularProduct.objects.get(id=product_id)  # to get the product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) #here  it will match cart id with session id. get the cart using the cart_id. [ we need to cart id from session.ie inside cookies there is session and it gives session id.. that session is taken as cart id]
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id =_cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity +=1   #if we add more than 1 cart item cart_item will increment
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,      # 1 because it is new cartitem
            cart  = cart,
        )
        cart_item.save()
    
    #return HttpResponse(cart_item.product)   #this is for checking weather the product name reach to cart
    #exit()
    
    return redirect('cart')


def remove_cart(request, product_id):                        # this function is used to reduce cart item while clicking minus button
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(PopularProduct,id=product_id)
    cart_item = CartItem.objects.get(product=product , cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')



def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(PopularProduct,id=product_id)        
    cart_item = CartItem.objects.get(product=product , cart=cart)
    cart_item.delete()
    return redirect('cart')
        
        
    
def cart(request, total=0, quantity=0, cart_items=None):           # to modify cart function and add items to cart
    try:
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
    return render(request,'store/cart.html',context)   