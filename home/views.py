from django.db.models import Q
from django.shortcuts import render
from products.models import Category, Product

def index(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    products = Product.objects.select_related("category").prefetch_related("product_images")

    if query:
        products = products.filter(
            Q(product_name__icontains=query)
            | Q(product_description__icontains=query)
            | Q(category__category_name__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "search_query": query,
        "selected_category": category_slug,
    }
    return render(request, 'home/index.html', context)