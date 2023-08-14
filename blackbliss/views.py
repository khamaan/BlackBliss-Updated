from django.shortcuts import render
from store.models import Product
from django.urls import reverse

def home(request):
    products = Product.objects.filter(is_available=True).order_by("-uploaded_date")
    for product in products:
        product.get_url = reverse('product_detail', kwargs={'category_slug': product.category.slug, 'product_slug': product.slug})
    context = {
        "products": products,
    }
    return render(request, "home.html", context)

