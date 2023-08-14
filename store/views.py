from django.shortcuts import render, redirect
from .models import Product
from category.models import Category
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import ReviewForm
from django.contrib import messages

# Create your views here.
def store(request, category_slug=None):
    if category_slug != None:
        categories = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=categories)
        paginator = Paginator(products, 3)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)
        products_count = products.count()
    else:
        products = Product.objects.filter(is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)
        products_count = products.count()
    context = {
        "products": paged_products,
        "product_count": products_count,
    }
    return render(request, "store/store.html", context)


def product_detail(request, category_slug, product_slug):
    single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    reviews = single_product.reviews.order_by('-created_at')
    
    if request.user.is_authenticated:
        user_reviews = reviews.filter(user=request.user).order_by('-created_at')[:3]
        other_reviews = reviews.exclude(user=request.user).order_by('-created_at')[:3]
    else:
        user_reviews = []
        other_reviews = reviews[:3]
    
    context = {
        "single_product": single_product,
        "reviews": user_reviews,
        "other_reviews": other_reviews,
    }
    return render(request, "store/product_details.html", context)

def search(request):
    context = {}
    if "keyword" in request.GET:
        keyword = request.GET.get("keyword")
        if keyword:
            products = Product.objects.order_by("-uploaded_date").filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()
            context = {
                "products": products,
                "product_count": product_count,
            }
    else:
        return redirect("store")
    return render(request, "store/store.html", context)


def submit_review(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thank you! Your review has been submitted.")
            return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)
        else:
            messages.error(request, "Oops! Something went wrong.")
    else:
        form = ReviewForm()

    return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

def product_reviews(request, product_id):
    product = Product.objects.get(id=product_id)
    reviews = product.reviews.all()
    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'store/product_reviews.html', context)

