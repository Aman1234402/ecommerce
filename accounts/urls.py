from django.urls import path
from accounts.views import (
    activate_email,
    add_to_cart,
    cart_view,
    login_page,
    logout_page,
    register_page,
    remove_cart_item,
    update_cart_item,
)

urlpatterns = [
    path('login/', login_page, name="login"),
    path('register/', register_page, name="register"),
    path('logout/', logout_page, name="logout"),
    path('activate/<email_token>/', activate_email, name="activate_email"),
    path('cart/', cart_view, name="cart"),
    path('cart/add/<slug:slug>/', add_to_cart, name="add_to_cart"),
    path('cart/item/<uuid:item_id>/update/', update_cart_item, name="update_cart_item"),
    path('cart/item/<uuid:item_id>/remove/', remove_cart_item, name="remove_cart_item"),
]
