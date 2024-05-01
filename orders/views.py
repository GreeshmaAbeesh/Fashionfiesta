from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from cart .models import CartItem,Cart
from .forms import OrderForm,AddressesForm,CouponForm
from .models import Order,OrderProduct,Payment,Addresses
from storeitem .models import PopularProduct
import datetime
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from decimal import Decimal
from coupons.models import Coupon



# Create your views here.

def payments(request):
    body = json.loads(request.body)
    print(body)
    


    order = Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])

    # store transaction detailsinsidew Payment model

    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],

    )
    payment.save()


    order.payment = payment
    order.is_ordered = True

    # Set order status as Completed
    order.status = 'Completed'
    

    order.save()

    # MOVE THE CART ITEMS TO ORDER PRODUCT TABLE
    #cart_items = CartItem.objects.filter(user=request.user)
    #print('cart_item :',cart_items)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # Redirect the user back to the store if the cart is empty or doesn't exist
        return redirect('store')
    
    cart_items = CartItem.objects.filter(cart=cart)
    print('cartitems: ',cart_items)


    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    # Reduce the quantity of the sold products
        product = PopularProduct.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    #clear the cart
        
    CartItem.objects.filter(user=request.user).delete()

    #send order received email to customer
    mail_subject = 'Thank you for your order'
    #print("enter into the mail")
    message = render_to_string('orders/order_recieved_email.html',{
        'user' : request.user,
        'order': order,
        
    })
    #print(message)
    to_email = request.user.email  # we got email from user and send to it
    send_email = EmailMessage(mail_subject, message ,to=[to_email])
    #print("message send to email",send_email,"to_email:",to_email)
    send_email.send()

    #send order number and transaction id back to send data method via jsonrespose
    data ={
        'order_number' : order.order_number,
        'transID' : payment.payment_id,

    }

    #return render(request,'orders/payments.html')
    return JsonResponse(data)
  
   
  

'''       # Get the cart associated with the current session

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # Redirect the user back to the store if the cart is empty or doesn't exist
        return redirect('store')
    
    cart_items = CartItem.objects.filter(cart=cart)
    print('cartitems: ',cart_items)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.is_ordered
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product.id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

    # Reduce the quantity of the sold products

    

    

   
    return render(request,'orders/payments.html')

'''

def _cart_id(request):                  # cart made as private
    cart = request.session.session_key  # inside cookies there is session and it gives session id.
    if not cart:                        # if there is no asession, it will create new session
        cart = request.session.create()
    return cart 


def place_order(request, total=0, quantity=0):
    
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
    #coupons = cart.coupons.first()
    #print('coupon is :',coupons)
    #If there's no coupon applied, discount is zero
    #discount = coupons.discount if coupons else Decimal(0)
    #print('discount is',discount)

   
    # Calculate the grand total after applying the discount
    grand_total = total
    tax = (2 * total)/100
    grand_total = float(grand_total) + tax 
    #print("GRANDTOTAL,TOTAL,TAX",grand_total,total,tax)
    #print('request.method=',request.method)

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
                #'coupons' : coupons,
                #'discount' : discount,
            }
            print('order number in place_order:',order_number)
            return render(request,'orders/payments.html',context)
        else:
            # If form is not valid, render the checkout page again with form errors
            return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items})

    else:
        return redirect('checkout')  # Redirect to checkout page for other HTTP methods


def order_complete(request):
    order_number  = request.GET.get('order_number')
    print('order_number in order_complete',order_number)
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price*i.quantity

        payment = Payment.objects.get(payment_id = transID)

        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'transID' : payment.payment_id,     #doubt
            'payment' : payment,
            'subtotal' : subtotal,
        }
        return render(request,'orders/order_complete.html',context)
    except (Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')
    
'''
def cash_on_delivery(request):
    if request.method == "POST":
        # Assuming you have a form that submits the order id
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)

        
        # Create a Payment instance
        payment = Payment.objects.create(
            user=request.user,
            payment_method='Cash on Delivery',
            amount_paid= grand_total,
            status='Pending'  # Assuming you initially set status as pending for cash on delivery orders
        )

        # Update the order with payment details
        order.payment_id = payment
        order.order_total = grand_total
        order.tax = tax
        order.status = 'Accepted'  # Assuming you change order status to accepted upon choosing cash on delivery
        order.save()

        # Mark order products as ordered
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            order_product.ordered = True
            order_product.save()

        return redirect('payment_successful')  # Redirect to payment successful page or any other page

    return render(request, 'orders/cod_order_complete.html')

def cash_on_delivery(request):
    return render(request, 'orders/cod_order_complete.html')
    '''
'''
def cash_on_delivery(request):
    print('request',request.method)
    if request.method == "POST":
        order_number = request.POST.get('order_number')
        print('order_number',order_number)
        transID = request.POST.get('payment_id')
        print('transID',transID)
        
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=False)
            print("order",order)
            order.is_ordered = True
            order.save()

            
            context = {
                'order': order,
                'transID': transID,  # Pass payment ID to template context
            }
            return render(request, 'orders/cod_order_complete.html', context)
        except Order.DoesNotExist:
            # Handle case where order is not found
            pass
'''
'''
159 
    # Fetch the selected address
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        if address_id:
            address = Addresses.objects.get(id=address_id)
        else:
            # If no address is selected, use the address from the form
            form = OrderForm(request.POST)
            if form.is_valid():
                address = Addresses.objects.create(
                    user=current_user,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    address_line_1=form.cleaned_data['address_line_1'],
                    address_line_2=form.cleaned_data['address_line_2'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    country=form.cleaned_data['country']
                )


'''
def cash_on_delivery(request):
    print('request',request.method)
    
    if request.method == "POST":
        order_number = request.POST.get('order_number')
        print('order_number',order_number)
        transID = request.POST.get('payment_id')
        print('transID',transID)
        
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # Redirect the user back to the store if the cart is empty or doesn't exist
        return redirect('store')
    
    cart_items = CartItem.objects.filter(cart=cart)
    print('cartitems: ',cart_items)


    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    # Reduce the quantity of the sold products
        product = PopularProduct.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    #clear the cart
        
    CartItem.objects.filter(user=request.user).delete()
   
    order.is_ordered = True
    order.status = 'Cash_on_delivery'
    order.save()

   
            
    context = {
                'order': order,
                'transID': transID,  # Pass payment ID to template context  
            }
    return render(request, 'orders/cod_order_complete.html', context)


def save_address(request):
    
    if request.method == 'POST':
        print("enter into  post")
        form = AddressesForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('save_address')  # Redirect to address list page

    form = AddressesForm()

    addresses = Addresses.objects.filter(user=request.user)
    context ={
        'form' : form,
        'addresses' : addresses,
    }
    
    return render(request,'orders/address.html',context)

def delete_address(request, address_id):
    address = get_object_or_404(Addresses, pk=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
    return redirect('save_address')  # Redirect to address list page after deletion

#@login_required
def address_list(request):
    addresses = Addresses.objects.filter(user=request.user)
    return render(request, 'orders/address_list.html', {'addresses': addresses})



'''
def save_address(request):
    if request.method == 'POST':
        form = AddressesForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('address_list')
    else:
        form = AddressesForm()
    addresses = Addresses.objects.filter(user=request.user)
    
    return render(request, 'orders/address.html', {'form': form,},{'addresses': addresses})



def address_list(request):
    addresses = Addresses.objects.filter(user=request.user)
    return render(request, 'orders/address_list.html', )
    
'''



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
    
            return coupon_activate(request)
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
        form = CouponForm(request.POST)  # request to recieve the post items(name,address,etc..) to Orderform in forms.py
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
            #data.first_name = request.POST.get('first_name')  # Directly access POST data
            #data.last_name = request.POST.get('last_name')
            # data.phone = request.POST.get('phone')
            #data.email = request.POST.get('email')
            # data.address_line_1 = request.POST.get('address_line_1')
            # data.address_line_2 = request.POST.get('address_line_2')
            # data.country = request.POST.get('country')
            # data.state = request.POST.get('state')
            # data.city = request.POST.get('city')
            # data.order_note = request.POST.get('order_note')
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
            print('order is ',order)

            context = {
                #'order' : order,
                'order' : data,
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
'''

def coupon_activate(request):
    current_user = request.user
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        return redirect('store')

    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    total = sum(item.product.price * item.quantity for item in cart_items)

    coupons = cart.coupons.first()
    discount = coupons.discount if coupons else Decimal(0)

    grand_total = total - discount
    tax = (2 * total) / 100
    grand_total = float(grand_total) + tax

    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            # Retrieve the existing order associated with the user
            order = Order.objects.filter(user=current_user, is_ordered=False).first()
            print('ORDER IS',order)
            if order:
                # Update order total with the discounted amount
                order.order_total = grand_total
                order.save()

                # Apply the coupon to the order's coupons
                cart.coupons.add(coupons)

                # Redirect to the payment page with updated details
                return redirect('payments')
    else:
        return redirect('checkout')

    context = {
        #'order' : order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'coupons': coupons,
        'discount': discount,
    }

    return render(request, 'orders/payments.html', context)
'''