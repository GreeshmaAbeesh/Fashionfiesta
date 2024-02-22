from django.contrib import admin
from .models import Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)} #prepopulated_fields attribute to automatically populate the slug field based on the value of the category_name field. This means that when you enter or modify the category_name in the Django admin, the slug field will be automatically filled based on the provided category_name.
    list_display=('category_name','slug')

admin.site.register(Category,CategoryAdmin)
