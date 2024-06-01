from django.contrib import admin
from .models import PopularProduct,ProductGallery,Variation,ReviewRating,ProductOffer


# Register your models here.

class ProductGalleryInline(admin.TabularInline):   #An inline model is a way to manage related models from the parent model's admin page.
    model = ProductGallery
    extra = 1      

class ProductOfferInline(admin.TabularInline):
    model = ProductOffer
    extra = 1


#when you navigate to the admin page for managing Product instances, you'll also see an inline section for managing related ProductGallery instances. This is a convenient way to handle related models without having to navigate to a separate admin page.
class PopularProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','modified_date','is_available')
    list_filter = ('is_available', 'created_date', 'modified_date')
    search_fields = ('product_name',)
    prepopulated_fields={'slug':('product_name',)}
    
    inlines = [ProductGalleryInline, ProductOfferInline]  # Add ProductOfferInline here


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','variation_image','is_active')
    list_editable = ('is_active',)  # is active is editable in admin page andit must be a list or tuple
    list_filter = ('product','variation_category','variation_value')
    



admin.site.register(PopularProduct,PopularProductAdmin)
admin.site.register(ProductGallery)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductOffer)

