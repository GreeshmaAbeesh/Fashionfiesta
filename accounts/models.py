from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have an username')
        
        user=self.model(
            email=self.normalize_email(email),  #if we enter any capitalletter email it will normalize ti small letter
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password) # inbuild function to save password
        user.save(using=self._db)
        return user


    def create_superuser(self,first_name,last_name,username,email,password):
        user = self.create_user(
            email=self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

    

class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=100,unique=True)
    phone_number = models.CharField(max_length=50)

    
    date_joined =models.DateTimeField(auto_now_add=True) # auto_now_add=True means set to current date and time
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)   #This field is a boolean (True/False) flag indicating whether a user has administrative privileges. The default=False parameter means that if this field is not explicitly set, its default value will be False.
    is_staff = models.BooleanField(default=False) # This boolean field indicates whether a user is a staff member (has access to the admin site). Similar to is_admin, the default value is set to False.
    is_active = models.BooleanField(default=False) # This field represents whether a user account is active or not. A user might be deactivated for various reasons, such as inactivity or a request to suspend the account. The default value is set to False.
    is_superadmin = models.BooleanField(default=False) #This boolean field indicates whether a user has superadmin privileges. Again, the default value is set to False.

    # for making email id as login username in custom managed admin panel 

    USERNAME_FIELD = 'email'       
    REQUIRED_FIELDS = ['username','first_name','last_name']

    objects=MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):    # if user is admin, he has all the permissions to do changes
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)     # one profile for one user
    address_line_1 = models.CharField(blank=True,max_length=100)
    address_line_2 = models.CharField(blank=True,max_length=100)
    profile_picture = models.ImageField(blank=True,upload_to='userprofile/')
    city = models.CharField(blank=True,max_length=100)
    state = models.CharField(blank=True,max_length=100)
    country = models.CharField(blank=True,max_length=100)

    def __str__(self):
        return self.user.first_name
    
    def full_address(self):
        return f"{self.address_line_1}{self.address_line_2}"
