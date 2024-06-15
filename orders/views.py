from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from cart .models import CartItem,Cart,Coupon
from .forms import OrderForm,AddressesForm,ReturnRequestForm,WalletDeductionForm
from .models import Order,OrderProduct,Payment,Addresses,Wallet,SalesReportNew
from storeitem .models import PopularProduct,ProductOffer
import datetime
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from decimal import Decimal
#from coupons.models import Coupon
from django.core.exceptions import ObjectDoesNotExist
from .models import ReturnRequest,BillingAddress
from django.db.models import Sum
import decimal
from django.db.models import F
from accounts .models import UserProfile
from django.utils import timezone
from datetime import datetime as mydatetime
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.http import Http404
#from django.http import FileResponse
#import io
#from reportlab.pdfgen import canvas
#from reportlab.lib.units import inch
#from reportlab.lib.pagesizes import letter
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView

from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone
from django.views.decorators.http import require_http_methods
#from datetime import datetime, date




# Create your views here.

def payments(request):
    if request.method == 'POST':
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
        print("Payment status ", payment.status)
        payment.save()

        if payment.status == "COMPLETED":
            order.payment = payment
            order.is_ordered = True

            # Set order status as Completed
            order.status = 'Completed'
        else:
            order.payment = payment
            order.is_ordered = False

            # Set order status as Completed
            order.status = 'Not_Completed'
            

        order.save()

        # MOVE THE CART ITEMS TO ORDER PRODUCT TABLE
        
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
        message = render_to_string('orders/order_recieved_email.html',{
            'user' : request.user,
            'order': order,
            
        })
        
        to_email = request.user.email  # we got email from user and send to it
        send_email = EmailMessage(mail_subject, message ,to=[to_email])
        send_email.send()

        #send order number and transaction id back to send data method via jsonrespose
        data ={
            'order_number' : order.order_number,
            'transID' : payment.payment_id,

        }

        return JsonResponse(data)
    return render(request,'orders/payments.html')
  



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
    

    
    grand_total = Decimal('0')
    tax = Decimal('0')
    discount = Decimal('0')
    coupon = None
    original_total = Decimal('0') # Initialize original_total

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
    print('quantity',quantity)

    if coupon:
        discount = (coupon.discount / 100) * total
        total -= discount

   
    # Fetch the user's wallet
    try:
        wallet = Wallet.objects.get(user=request.user)
        print('wallet is', wallet)
    except Wallet.DoesNotExist:
        # If Wallet object doesn't exist, create one for the user
        wallet = Wallet.objects.create(user=request.user)

    # Check if there is any deduction in the wallet
    wallet_deduction = wallet.deduction if wallet else Decimal('0')
    print('deducted amount',wallet_deduction)





    # Calculate the grand total after applying the discount
    grand_total = total
    tax = (Decimal('2') * total) / Decimal('100')
    grand_total += tax - wallet_deduction
    savings = original_total - grand_total  # Calculate the total savings
    print("GRANDTOTAL,TOTAL,TAX",grand_total,total,tax)
    #print('request.method=',request.method)

    # Remove coupon ID from session if it exists
    if 'coupon_id' in request.session:
        del request.session['coupon_id']



    if request.method == 'POST':
        
        address_id = request.POST.get('address_id')

        if not address_id:
            address = None
        else:
            try:
                address = Addresses.objects.get(id=address_id, user=current_user)
            except Addresses.DoesNotExist:
                address = None


        if address is None:
            form = OrderForm(request.POST)  # request to recieve the post items(name,address,etc..) to Orderform in forms.py
            print('inside post form')
            if form.is_valid():
                print('inside form is valid')
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
                data.discount = discount  # Save the discount amount
                data.ip = request.META.get('REMOTE_ADDR')
                data.status = "Not_Completed"
                print("data valid iside place order before data save")
                data.save()  #after save we got a data id
                print("data valid iside place order",data)
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
                
                # Reset the wallet deduction after order placement
                wallet.deduction = 0
                wallet.save()
                
                context = {
                    #'order' : order,
                    'order' : order,
                    'cart_items' : cart_items,
                    'total' : total,
                    'tax' : tax,
                    'grand_total' : grand_total,
                    'wallet_deduction' : wallet_deduction,
                    'coupon': coupon,
                    'discount': discount,
                    'savings': savings,
                }
                print('order number in place_order:',order_number)
                return render(request,'orders/payments.html',context)
            else:
                print('else condition order number in place_order:')
                # If form is not valid, render the checkout page again with form errors
                return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items})
        else:
            data = Order()
            data.user = current_user
            data.first_name = address.first_name
            data.last_name = address.last_name
            data.phone = address.phone
            data.email = address.email
            data.address_line_1 = address.address_line_1
            data.address_line_2 = address.address_line_2
            data.country = address.country
            data.state = address.state
            data.city = address.city
            data.order_note = address.order_note
            data.order_total = grand_total
            data.tax = tax
            data.discount = discount  # Save the discount amount
            data.ip = request.META.get('REMOTE_ADDR')
            data.status = "Not_Completed"
            data.save()            
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
            
            # Reset the wallet deduction after order placement
            wallet.deduction = 0
            wallet.save()
            
            context = {
                #'order' : order,
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
                'wallet_deduction' : wallet_deduction,
                'coupon': coupon,
                'discount': discount,
                'savings': savings,
            }
            print('order number in place_order:',order_number)
            return render(request,'orders/payments.html',context)

    else:
        return redirect('checkout')  # Redirect to checkout page for other HTTP methods


def generate_pdf(request, order_number):
    try:
        # Fetch order data
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order=order)

        # Calculate subtotal
        subtotal = sum(item.product_price * item.quantity for item in ordered_products)

        # Prepare context for the template
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'subtotal': subtotal,
        }

        # Render template
        template_path = 'orders/invoice_template.html'  # Update with your invoice template path
        template = get_template(template_path)
        html = template.render(context)

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{order.order_number}_invoice.pdf"'

        # Generate PDF file
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response

    except Order.DoesNotExist:
        return HttpResponse('Order not found.')
    

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    if request.GET.get('format') == 'pdf':
        return generate_pdf(request, order_number)

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order=order)

        subtotal = sum(item.product_price * item.quantity for item in ordered_products)
        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

    

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
    
     # Calculate the total order amount
    total_amount = sum(item.product.price * item.quantity for item in CartItem.objects.filter(cart=cart))
    
    # Check if the total amount exceeds Rs. 1000
    if total_amount > 1000:
        messages.error(request, "COD not allowed for orders above Rs. 1000")
        return redirect('checkout')
    
    
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
             # Redirect to payment page with the saved address ID
            return redirect('save_address')

    form = AddressesForm()

    addresses = Addresses.objects.filter(user=request.user)
    context ={
        'form' : form,
        'addresses' : addresses,
    }
    print("context",context)
    return render(request,'store/nav_address.html',context)

@require_http_methods(["DELETE"])
def delete_address(request, address_id):
    address = get_object_or_404(Addresses, pk=address_id, user=request.user)
    address.delete()
    return JsonResponse({'success': True})


def edit_address(request, address_id):
    address = get_object_or_404(Addresses, pk=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressesForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('save_address')

    form = AddressesForm(instance=address)
    context = {
        'form': form,
        'address': address,
    }
    return render(request, 'store/edit_address.html', context)
    


def cancel_order(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    
    
    # Implement your cancellation logic here
    # For example, you can update the order status to "Cancelled"
    order.status = 'Cancelled'
    order.save()

    # Decrease the dashboard count for canceled ordered items
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.orders_count = F('orders_count') - 1
    #user_profile.ordered_items_count = F('ordered_items_count') - ordered_items_count
    user_profile.save()

    try:
        wallet = Wallet.objects.get(user=request.user)
        print('wallet is', wallet)
    except Wallet.DoesNotExist:
        # If Wallet object doesn't exist, create one for the user
        wallet = Wallet.objects.create(user=request.user)


    # Query the return requests associated with the current user
    return_requests = ReturnRequest.objects.filter(order__user=request.user)
    print('order is',return_requests)
    total_refunded_amount = sum(return_request.order.order_total for return_request in return_requests)

    # Query canceled orders associated with the current user
    canceled_orders = Order.objects.filter(user=request.user, status='Cancelled')
    total_canceled_amount = canceled_orders.aggregate(total_canceled_amount=Sum('order_total'))['total_canceled_amount'] or 0

    # Calculate total refunded amount and total canceled amount
    total_refund_and_canceled_amount = total_refunded_amount + total_canceled_amount


    if total_refund_and_canceled_amount:
        # Convert total_refunded_amount to a decimal.Decimal object
        total_amount_decimal = decimal.Decimal(str(total_refund_and_canceled_amount))

        # Add the total refunded amount to the user's wallet balance
        wallet.balance = total_amount_decimal
        wallet.save()
        
    return redirect('my_orders') 



def return_request(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    print('order details:',order)
   
   
    if request.method == 'POST':
        print('Request method is POST')
        form = ReturnRequestForm(request.POST)
        print('given form is',form)
        if form.is_valid():
            return_reason = form.cleaned_data['return_reason']
            print('returned reason',return_reason)
            # Create a return request object
            ReturnRequest.objects.create(order=order,return_reason=return_reason)
            # Update the order status to "Return Requested"
            order.status = 'Returned'
            order.is_returned = True
            order.save()

            
            # Calculate refunded amount and add it to user's wallet balance
            refunded_amount = order.order_total  # Assuming full refund
            print('refunded amount is:',refunded_amount)
           
            try:
                wallet = Wallet.objects.get(user=request.user)
                print('wallet is', wallet)
            except Wallet.DoesNotExist:
                # If Wallet object doesn't exist, create one for the user
                wallet = Wallet.objects.create(user=request.user)

            # Query the return requests associated with the current user
            return_requests = ReturnRequest.objects.filter(order__user=request.user)
            print('order is',return_requests)
            total_refunded_amount = sum(return_request.order.order_total for return_request in return_requests)

            # Query canceled orders associated with the current user
            canceled_orders = Order.objects.filter(user=request.user, status='Cancelled')
            total_canceled_amount = canceled_orders.aggregate(total_canceled_amount=Sum('order_total'))['total_canceled_amount'] or 0

            # Calculate total refunded amount and total canceled amount
            total_refund_and_canceled_amount = total_refunded_amount + total_canceled_amount


            if total_refund_and_canceled_amount:
                # Convert total_refunded_amount to a decimal.Decimal object
                total_amount_decimal = decimal.Decimal(str(total_refund_and_canceled_amount))

                # Add the total refunded amount to the user's wallet balance
                wallet.balance = total_amount_decimal
                wallet.save()
            #messages.success(request, 'Return request submitted successfully.')
            return redirect('my_orders')
    else:
        form = ReturnRequestForm()
        print('This is else part')

    
    context = {
        'form': form,
       
       
    }
    return render(request,'accounts/return_request.html',context)
   

def wallet(request):
   
    try:
        wallet = Wallet.objects.get(user=request.user)
        print('wallet is', wallet)
    except Wallet.DoesNotExist:
        # If Wallet object doesn't exist, create one for the user
        wallet = Wallet.objects.create(user=request.user)

    
    if request.method == 'POST':
        deduction_form = WalletDeductionForm(request.POST)
        if deduction_form.is_valid():
            deduction_amount = deduction_form.cleaned_data['deduction_amount']
            print('deducting amount given', deduction_amount )
            wallet = Wallet.objects.get(user=request.user)
            if deduction_amount <= wallet.balance:
                # Deduct the amount from the wallet balance
                print('wallet balance before deducting',wallet.balance)
                
                walletModifiedAmt = wallet.balance - deduction_amount
                walletCurrentAmt = decimal.Decimal(str(walletModifiedAmt))
                wallet.deduction = deduction_amount
                wallet.balance = walletCurrentAmt
                print("wallet.balance , walletCurrentAmt",wallet.balance, walletCurrentAmt)
                wallet.save()
                print('wallet balance after deducting',wallet.balance)
                #return render(request,'store/checkout.html') # Redirect to the payment page
                #return redirect('checkout', wallet_id=wallet.id)

                #return render(request, 'orders/wallet.html', {'wallet': wallet,'return_requests': return_requests, 'canceled_orders': canceled_orders,'deduction_form': deduction_form})
    else:
        deduction_form = WalletDeductionForm()
    print('wallet balance in end deducting',wallet.balance)
    # Pass the wallet object to the template
    return render(request, 'orders/wallet.html', {'wallet': wallet,'deduction_form': deduction_form})





def sales_report(request):
    # Default start and end dates for custom date range
    start_date = end_date = None
    
    # Default date range selection
    date_range = request.GET.get('date_range', 'custom')
    
    # Get today's date
    today = timezone.now().date()
    
    # Set start and end dates based on date range selection
    if date_range == 'daily':
        start_date = end_date = today
    elif date_range == 'weekly':
        start_date = today - timezone.timedelta(days=today.weekday())
        end_date = start_date + timezone.timedelta(days=6)
    elif date_range == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:
        start_date = today.replace(day=1)
        end_date = today
    
    # Get orders within the selected date range
    orders = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).order_by('-created_at')

    # Calculate total sales amount
    total_sales_amount = round(orders.aggregate(total_sales=Sum('order_total'))['total_sales'] or 0, 2)
    
    # Calculate total discount
    total_discount = orders.aggregate(total_discount=Sum('discount'))['total_discount'] or 0
    
    # Calculate total coupon count
    total_coupon_count = orders.exclude(coupon=None).count()
    
    # Calculate overall sales count
    overall_sales_count = orders.count()

    # Check if SalesReport instance already exists for the specified date range
    sales_report_instance, created = SalesReportNew.objects.get_or_create(
        start_date=start_date,
        end_date=end_date,
        date_range=date_range,
        defaults={
            'overall_sales_count': overall_sales_count,
            'total_sales_amount': total_sales_amount,
            'total_discount': total_discount,
            'total_coupon_count': total_coupon_count
        }
    )
    if not created:
        sales_report_instance.overall_sales_count = overall_sales_count
        sales_report_instance.total_sales_amount = total_sales_amount
        sales_report_instance.total_discount = total_discount
        sales_report_instance.total_coupon_count = total_coupon_count
        sales_report_instance.save()
    
    context = {
        'orders': orders,
        'sales_report_instance': sales_report_instance,
        'total_sales_amount': total_sales_amount,
        'total_discount': total_discount,
        'total_coupon_count': total_coupon_count,
        'overall_sales_count': overall_sales_count,
        'start_date': start_date,
        'end_date': end_date,
        'date_range': date_range,
    }
    
    return render(request, 'sales_report.html', context)
