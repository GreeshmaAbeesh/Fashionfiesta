from django.contrib import admin
from .models import PopularProduct,ProductGallery


# Register your models here.

class ProductGalleryInline(admin.TabularInline):   #An inline model is a way to manage related models from the parent model's admin page.
    model = ProductGallery
    extra = 1      


#when you navigate to the admin page for managing Product instances, you'll also see an inline section for managing related ProductGallery instances. This is a convenient way to handle related models without having to navigate to a separate admin page.
class PopularProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','modified_date','is_available')
    prepopulated_fields={'slug':('product_name',)}
    inlines = [ProductGalleryInline]

admin.site.register(PopularProduct,PopularProductAdmin)
admin.site.register(ProductGallery)
