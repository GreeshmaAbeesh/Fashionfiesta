from django.contrib import admin
from .models import Product,ProductImage


# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to display for uploading additional images


class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','price','stock','category','modified_date','is_available')
    prepopulated_fields={'slug':('product_name',)}
    inlines = [ProductImageInline]



admin.site.register(Product,ProductAdmin)