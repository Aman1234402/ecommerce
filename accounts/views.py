import logging
from smtplib import SMTPException

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlencode
from .models import CartItem, Profile
from products.models import Product

# Create your views here.

logger = logging.getLogger(__name__)

def login_page(request):

    if request.method == 'POST':
            next_url = request.POST.get("next", "")
            email = request.POST.get('email')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username=email)
    
            if not user_obj.exists():
               messages.warning(request, 'Account not found.')
               return _login_retry_redirect(request, next_url)

            if not user_obj[0].profile.is_email_verified:
               messages.warning(request, 'Your account is not verified.')
               return _login_retry_redirect(request, next_url)
               
            user_obj = authenticate(request, username=email, password=password)
            if user_obj:
                login(request, user_obj)
                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)
                return redirect("index")
    
            messages.warning(request, 'Invalid Credentials')
            return _login_retry_redirect(request, next_url)
    
    return render(
        request,
        'accounts/login.html',
        {"next_url": request.GET.get("next", "")},
    )

def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=email)

        if user_obj.exists():
           messages.warning(request, 'Email is already taken.')
           return HttpResponseRedirect(request.path_info)

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            messages.error(
                request,
                'Email delivery is not configured. Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD.',
            )
            return HttpResponseRedirect(request.path_info)

        try:
            with transaction.atomic():
                user_obj = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=email,
                )
                user_obj.set_password(password)
                user_obj.save()
        except (SMTPException, OSError):
            logger.exception('Failed to send the account activation email to %s', email)
            messages.error(request, 'We could not send the verification email. Please try again.')
            return HttpResponseRedirect(request.path_info)

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/register.html')

def activate_email(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invaild Email token')


@login_required(login_url="login")
def cart_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    items = list(
        CartItem.objects.filter(profile=profile)
        .select_related("product", "size_variant")
        .prefetch_related("product__product_images")
    )
    return render(
        request,
        "accounts/cart.html",
        {"cart_items": items, "cart_total": sum(item.line_total for item in items)},
    )


@require_POST
def add_to_cart(request, slug):
    if not request.user.is_authenticated:
        messages.info(request, "Sign in to add this product to your cart.")
        return redirect_to_login(
            reverse("get_product", args=[slug]),
            login_url=reverse("login"),
        )

    product = get_object_or_404(Product.objects.prefetch_related("size_variant"), slug=slug)
    quantity = _posted_quantity(request)
    if quantity is None:
        messages.error(request, "Enter a quantity of at least 1.")
        return redirect("get_product", slug=product.slug)

    size_variant_id = request.POST.get("size_variant", "")
    size_variant = None
    if product.size_variant.exists():
        if not size_variant_id:
            messages.error(request, "Choose a size before adding this product to your cart.")
            return redirect("get_product", slug=product.slug)
        size_variant = product.size_variant.filter(uid=size_variant_id).first()
        if size_variant is None:
            messages.error(request, "That size is not available for this product.")
            return redirect("get_product", slug=product.slug)

    profile, _ = Profile.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(
        profile=profile,
        product=product,
        size_variant=size_variant,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity
        item.save(update_fields=["quantity", "updated_at"])

    messages.success(request, "Added to your cart.")
    return redirect("cart")


@login_required(login_url="login")
@require_POST
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, profile__user=request.user)
    quantity = _posted_quantity(request)
    if quantity is None:
        messages.error(request, "Enter a quantity of at least 1.")
    else:
        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])
        messages.success(request, "Cart quantity updated.")
    return redirect("cart")


@login_required(login_url="login")
@require_POST
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, profile__user=request.user)
    item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect("cart")


@login_required(login_url="login")
@require_POST
def logout_page(request):
    logout(request)
    messages.success(request, "You have been signed out.")
    return redirect("index")


def _posted_quantity(request):
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        return None
    return quantity if quantity >= 1 else None


def _login_retry_redirect(request, next_url):
    if next_url:
        query_string = urlencode({"next": next_url})
        return HttpResponseRedirect(f"{request.path_info}?{query_string}")
    return HttpResponseRedirect(request.path_info)