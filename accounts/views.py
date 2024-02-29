from django.shortcuts import render,redirect
from .forms import Registrationform
from .models import Account
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

            #messages.success(request, 'Thank you for your registration.Please verify with the link in your gmail')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = Registrationform()
    context = {
        'form' : form,  # form variable available in register.html
    }
    return render(request,'accounts/register.html',context)

'''
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Activate the user
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')
    else:
        return HttpResponse('Activation link is invalid or expired.')
                  

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
'''

def login(request):
     
     if request.method=='POST':
          email=request.POST['email']
          password=request.POST['password']

          user=auth.authenticate(email=email,password=password)
          
          if user is not None:
              auth.login(request,user)
              return redirect('home')
          else:
              messages.error(request,'Invalid Username or password')
              return redirect('login')
     else:
       return render(request,"accounts/login.html")


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



