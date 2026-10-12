from django.shortcuts import get_object_or_404, render
from products.models import Product


def get_product(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("size_variant", "product_images"),
        slug=slug,
    )
    context = {"product": product}
    selected_size_id = request.GET.get("size")
    if selected_size_id:
        selected_size = get_object_or_404(product.size_variant, uid=selected_size_id)
        context["selected_size"] = str(selected_size.uid)
        context["updated_price"] = product.price + selected_size.price

    return render(request, "product/product.html", context=context)
