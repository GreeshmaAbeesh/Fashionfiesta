from django.shortcuts import render,redirect
from cart .models import Cart,CartItem
from django.contrib import messages
from .models import Coupon
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from orders.views import place_order


# Create your views here.


def _cart_id(request):                  # cart made as private
    cart = request.session.session_key  # inside cookies there is session and it gives session id.
    if not cart:                        # if there is no asession, it will create new session
        cart = request.session.create()
    return cart 



def coupon(request):
    #Coupon.activate_default_coupon()

   
    if request.method == "POST":
        code = request.POST.get("coupon_code")
        print('entered code:',code)

        # Check if the coupon code is provided
        if not code:
            messages.error(request, "Please provide a coupon code.")
            print("Please provide a coupon code.")
            return redirect("checkout")  # Redirect back to checkout if no coupon code provided

        # Retrieve the coupon from the database
        coupon = Coupon.objects.filter(code=code, active=True).first()
        print('coupon is :',coupon)

        if not coupon:
            messages.error(request, "Invalid coupon code.")
            print('given value is not coupon')
            return redirect("checkout")
        

        # Check if the code is the default code
        default_code = "CODE123"
        if code == default_code:
            messages.success(request, "Default coupon activated successfully.")
            print('coupon activated successfully')
           
            cart = Cart.objects.get(cart_id=_cart_id(request))

            # Calculate the order total based on the sum of subtotals of all cart items
            cart_items = CartItem.objects.filter(cart=cart)
            order_total = sum(item.sub_total() for item in cart_items)
            print("total order",order_total)

            # Ensure the coupon discount does not exceed the order total
            discount = min(coupon.discount, order_total)
            print('discount value', discount)

            cart.order_total = order_total - discount  # Subtract the discount, not coupon.discount
            print('cart.order_total is', cart.order_total)
            cart.save()

            # Add the coupon to the order's coupons
            cart.coupons.add(coupon)
            print('coupon successfully applied')
            messages.success(request, "Coupon applied successfully.")
    
            return redirect('coupon_activate')
    return redirect('checkout')            

            # Redirect to place_order view with updated details
            #return redirect(reverse('place_order', kwargs={'total': order_total, 'grand_total': grand_total}))
    
    
    #return render(request,'orders/payments.html',{'order_total': cart.order_total})


def coupon_activate(request,total=0, quantity=0):
    current_user = request.user
    print('current user inside place order',current_user)

    # Get the cart associated with the current session
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # Redirect the user back to the store if the cart is empty or doesn't exist
        return redirect('store')
    # Fetch the selected address


    #if cart count is less than or equal to 0, then redirect back to shop page
    cart_items = CartItem.objects.filter(cart=cart,is_active=True)
    print('cart_items = ',cart_items)
    cart_count = cart_items.count()
    print('cartcount = ',cart_count,cart_items)
    if cart_count <= 0:
        return redirect('store')
    
    
    grand_total =0
    tax = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    print('quantity',quantity)

    
    #coupons = Coupon.objects.all()
    #print('couponcode',coupons)
    #Fetch the coupon applied to the cart
    coupons = cart.coupons.first()
    print('coupon is :',coupons)
    #If there's no coupon applied, discount is zero
    discount = coupons.discount if coupons else Decimal(0)
    print('discount is',discount)

   
    # Calculate the grand total after applying the discount
    grand_total = total - discount
    tax = (2 * total)/100
    grand_total = float(grand_total) + tax 
    print("GRANDTOTAL,TOTAL,TAX",grand_total,total,tax)
    print('request.method=',request.method)

    if request.method == 'POST':
        form = OrderForm(request.POST)  # request to recieve the post items(name,address,etc..) to Orderform in forms.py
        #print('inside post',form)
        if form.is_valid():
            # store all the billing information inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']  # recieve files values from request.POST
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()  #after save we got a data id
            #print(data)
            # generate order_id(ordernumber)
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d') #20240314
            print(current_date)
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            print('data',data)
            
            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)  # true when payment is successful
            context = {
                #'order' : order,
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
                'coupons' : coupons,
                'discount' : discount,
            }
            print('order number in place_order:',order_number)
            return render(request,'orders/payments.html',context)
        else:
            # If form is not valid, render the checkout page again with form errors
            return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items})

    else:
        return redirect('checkout')  # Redirect to checkout page for other HTTP methods
