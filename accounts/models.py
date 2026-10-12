from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile')


class CartItem(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="cart_items")
    size_variant = models.ForeignKey(
        "products.SizeVariant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("profile", "product", "size_variant"),
                condition=models.Q(size_variant__isnull=False),
                name="unique_cart_item_variant",
            ),
            models.UniqueConstraint(
                fields=("profile", "product"),
                condition=models.Q(size_variant__isnull=True),
                name="unique_cart_item_no_variant",
            ),
        ]

    @property
    def unit_price(self):
        return self.product.price + (self.size_variant.price if self.size_variant_id else 0)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"

@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    if created:
        email_token = str(uuid.uuid4())
        Profile.objects.create(user=instance, email_token=email_token)
        send_account_activation_email(instance.email, email_token)