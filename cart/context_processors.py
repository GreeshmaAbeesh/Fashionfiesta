from .models import Cart,CartItem
from cart.views import _cart_id



def counter(request):
    cart_count=0
    if 'admin' in request.path:     #if we are inside the admin dont want to see anything in cart.so pass empty dictionary
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity                # if we are addind cart item it will increment
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)

