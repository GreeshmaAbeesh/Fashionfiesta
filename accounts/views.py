
from django.shortcuts import render,redirect,get_object_or_404
from .forms import Registrationform,Userform,UserProfileForm
from .models import Account,UserProfile
from django.contrib import messages,auth
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from datetime import datetime,timedelta
from orders.models import Order,OrderProduct,Payment
from cart.views import _cart_id
from cart.models import Cart,CartItem,PopularProduct
from django.db.models import F



# Create your views here.

@never_cache


def register(request):
    if request.method == 'POST':
        form = Registrationform(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']   # to fetch the data
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)  # inside create user pass all the fields
            user.phone_number =  phone_number
            user.save()

            # create user Profile
            profile = UserProfile()
            profile.user_id = user.id   # the id created when user signup is connecting with profile
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user' : user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # here encoding the primary key and nobody can see it and it decode when it activate
                'token' : default_token_generator.make_token(user)    # make token create token and pass to the user
            })
            to_email = email  # we got email from user and send to it
            send_email = EmailMessage(mail_subject, message ,to=[to_email])
            send_email.send()

            messages.success(request, 'Thank you for your registration.Please verify with the link in your gmail')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = Registrationform()
    context = {
        'form' : form,  # form variable available in register.html
    }
    return render(request,'accounts/register.html',context)


def login(request):
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']

        user=auth.authenticate(email=email,password=password)

        if user is not None:
            auth.login(request,user)
            #messages.success(request,'You are now logged in')
            return redirect('home')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')
    return render(request,'accounts/login.html')




@login_required(login_url='login') # we can logged out the system when you are log in.
def logout(request):
    auth.logout(request) 
    messages.success(request,'You are logged out.')
    return redirect('login')




def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()   # decode the uidb and the value store in uid and it become primary key of user
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations your account is activated.' )
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.' )
        return redirect('register')



def forgotpassword(request):
    if request.method == 'POST':
        email =  request.POST['email']    #this email we get from forgotpassword form
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email)

            #Reset password email(same as email activation)
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user' : user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # here encoding the primary key and nobody can see it and it decode when it activate
                'token' : default_token_generator.make_token(user)    # make token create token and pass to the user
            })
            to_email = email  # we got email from user and send to it
            send_email = EmailMessage(mail_subject, message ,to=[to_email])
            send_email.send()

            messages.success(request,'Resetting password sent to your email')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist')
            return redirect('forgotpassword')

    return render(request, 'accounts/forgotpassword.html')


def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()   # decode the uidb and the value store in uid and it become primary key of user
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid     #save uid here because we use this uid when reset password
        messages.success(request,'Reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link has been expired!') 
        return redirect('login')
    

def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']                  # for reset- uid saved only when you coming through validation link
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')   # for taking saved uid
            user = Account.objects.get(pk=uid)
            user.set_password(password)                   #we need to set password because simple saving makes error in django. if you set password ,django's inbuilt function take the password and save it in hash format
            user.save()
            messages.success(request,'Password Reset Successfully')
            return redirect('login')
        else:
            messages.error(request,'Password not matching')
            return redirect('resetpassword')
    
    else:
        return render(request, 'accounts/resetpassword.html')   # is the methosd is not POST this template will load


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True, status__in=['Completed','Cash_on_delivery'])
    orders_count = orders.count()

    
    context={
        'orders_count' : orders_count,
        
    }
    return render(request, 'accounts/dashboard.html',context)


@login_required(login_url = 'login')    
def my_orders(request):
    orders =  Order.objects.filter(user=request.user,is_ordered=True, status__in=['Completed','Cash_on_delivery']).order_by('-created_at')
   
    context = {
        'orders' : orders,
        
    }

    return render(request,'accounts/my_orders.html',context)


@login_required(login_url = 'login')
def edit_profile(request):
    
    userprofile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = Userform(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your profile has been updated')
            return redirect('edit_profile')
    else:
        user_form = Userform(instance=request.user)    # for seeing the existing data inside the form
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
        'userprofile' : userprofile,
    }

    return render(request,'accounts/edit_profile.html',context)


@login_required(login_url = 'login')
def change_password(request):
    if request.method == 'POST':
        
        current_password = request.POST['current_password']  # take this current password from change_password.html
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        print('current_password ',current_password)
        user = Account.objects.get(username__exact=request.user.username)
        print('user',user)
        print('current_password,newpassword,confirmpassword:',current_password,new_password,new_password)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            print("success",success)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)   #use this line is you want to logut after reset password
                messages.success(request,'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request,'Please enter valid current password')
                print('enter valid password')
                return redirect('change_password')
        else:
            messages.error(request,'Password doesnt match')
            return redirect('change_password')
        
    return render(request,'accounts/change_password.html')


@login_required(login_url = 'login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0 
    for i in order_detail:
        subtotal = i.product_price * i.quantity
    context = {
        'order_detail' : order_detail,
        'order' : order,
        'subtotal' : subtotal,
    }
    print('order:',order_detail)
    return render(request,'accounts/order_detail.html',context)



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
    return redirect('my_orders') 

