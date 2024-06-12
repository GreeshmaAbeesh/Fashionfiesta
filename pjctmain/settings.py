"""
Django settings for pjctmain project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-xqcidul21v5d*f(0&4hbs@8o5)m1qojv79$=gl-do31r37nxk9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['fashionfiesta-course-new-env.eba-tzhfv34i.us-west-2.elasticbeanstalk.com']


# Application definition

INSTALLED_APPS = [
    'admin_soft.apps.AdminSoftDashboardConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'category',
    'accounts',
    'storeitem',
    'cart',
    'django_otp.plugins.otp_totp',
    'django_otp',
    #'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #'allauth.socialaccount.providers.google',
    #'allauth.socialaccount.providers.facebook',
    'customadmin',
    'orders',
    #'coupons',
    'wishlist',
    'easy_pdf',
    
    
    
    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
]

ROOT_URLCONF = 'pjctmain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_links',  # this menu_link available to all the templates.for that we using context processors
                'cart.context_processors.counter',
                
            ],
        },
    },
]

WSGI_APPLICATION = 'pjctmain.wsgi.application'

AUTH_USER_MODEL ='accounts.Account'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fashionfiestanew',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',    # Set to your database host if not running locally
        'PORT': '5432',         # Set to your database port if different
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT=BASE_DIR /'static'
STATICFILES_DIRS=[
    'pjctmain/static',
    #'custom_admin/static',
]



MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR /'media'
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field


from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: "danger",         # for showing seperate messages from django framework
    
}

# SMTP configuration .     SMTP (Simple Mail Transfer Protocol) configuration, which is commonly used for sending emails in a Python application.
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587    #The port number used for connecting to the SMTP server. For Gmail with TLS, the common port is 587.
EMAIL_HOST_USER = 'greeshmaps1992@gmail.com'
EMAIL_HOST_PASSWORD = 'ffxbnxqquhraquxt'
EMAIL_USE_TLS = True    #This is a boolean indicating whether to use TLS (Transport Layer Security) when connecting to the SMTP server. 
#EMAIL_USE_SSL = 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SUPERUSER_USERNAME = 'greeshma'
SUPERUSER_PASSWORD = 'greeshma' 



AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',

]



#LOGIN_REDIRECT_URL = 'home'