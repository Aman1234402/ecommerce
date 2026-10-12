from django.db.models import Sum

from .models import CartItem


def cart_count(request):
    if not request.user.is_authenticated:
        return {"cart_count": 0}
    total = CartItem.objects.filter(profile__user=request.user).aggregate(total=Sum("quantity"))["total"]
    return {"cart_count": total or 0}
