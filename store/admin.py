from django.contrib import admin
from .models import Product, ReviewRating
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display=['product_name','images','slug','price','stock','description']
    prepopulated_fields={'slug':('product_name',)}
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display=['product','rating','review','subject','user']
admin.site.register(Product,ProductAdmin)
admin.site.register(ReviewRating,ReviewRatingAdmin)