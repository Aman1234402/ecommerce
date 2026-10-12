from django.contrib import admin

# Register your models here.
from .models import CartItem, Profile

admin.site.register(Profile)
admin.site.register(CartItem)
