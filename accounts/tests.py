from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import CartItem
from products.models import Category, Product, SizeVariant


class LoginPageTests(TestCase):
    @patch("accounts.models.send_account_activation_email")
    def test_verified_user_can_log_in_with_registered_email(self, send_email):
        email = "customer@example.com"
        user = get_user_model().objects.create_user(
            username=email,
            email=email,
            password="correct-horse-battery-staple",
        )
        user.profile.is_email_verified = True
        user.profile.save(update_fields=["is_email_verified"])

        response = self.client.post(
            "/accounts/login/",
            {"email": email, "password": "correct-horse-battery-staple"},
        )

        self.assertRedirects(response, "/", fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
        send_email.assert_called_once()

    @patch("accounts.models.send_account_activation_email")
    def test_login_returns_to_a_safe_next_url(self, send_email):
        email = "redirect-customer@example.com"
        user = get_user_model().objects.create_user(
            username=email,
            email=email,
            password="correct-horse-battery-staple",
        )
        user.profile.is_email_verified = True
        user.profile.save(update_fields=["is_email_verified"])

        response = self.client.post(
            reverse("login"),
            {
                "email": email,
                "password": "correct-horse-battery-staple",
                "next": reverse("cart"),
            },
        )

        self.assertRedirects(response, reverse("cart"), fetch_redirect_response=False)
        send_email.assert_called_once()

    @patch("accounts.models.send_account_activation_email")
    def test_login_ignores_external_next_url(self, send_email):
        email = "external-redirect-customer@example.com"
        user = get_user_model().objects.create_user(
            username=email,
            email=email,
            password="correct-horse-battery-staple",
        )
        user.profile.is_email_verified = True
        user.profile.save(update_fields=["is_email_verified"])

        response = self.client.post(
            reverse("login"),
            {
                "email": email,
                "password": "correct-horse-battery-staple",
                "next": "https://example.invalid/",
            },
        )

        self.assertRedirects(response, reverse("index"), fetch_redirect_response=False)
        send_email.assert_called_once()


class CartViewTests(TestCase):
    def setUp(self):
        with patch("accounts.models.send_account_activation_email"):
            self.user = get_user_model().objects.create_user(
                username="cart-customer@example.com",
                email="cart-customer@example.com",
                password="correct-horse-battery-staple",
            )
        self.profile = self.user.profile
        category = Category.objects.create(category_name="Shoes", slug="shoes")
        self.product = Product.objects.create(
            product_name="Everyday Sneakers",
            slug="everyday-sneakers",
            category=category,
            price=100,
            product_description="Comfortable everyday sneakers.",
        )
        self.size = SizeVariant.objects.create(size_name="M", price=50)
        self.product.size_variant.add(self.size)
        self.client.force_login(self.user)

    def test_add_to_cart_saves_quantity_and_size_price(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.product.slug]),
            {"quantity": "2", "size_variant": str(self.size.uid)},
        )

        item = CartItem.objects.get(profile=self.profile, product=self.product)
        self.assertRedirects(response, reverse("cart"), fetch_redirect_response=False)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, 150)
        self.assertEqual(item.line_total, 300)

    def test_adding_same_variant_increments_existing_item(self):
        url = reverse("add_to_cart", args=[self.product.slug])
        data = {"quantity": "2", "size_variant": str(self.size.uid)}

        self.client.post(url, data)
        self.client.post(url, data)

        self.assertEqual(CartItem.objects.get(profile=self.profile).quantity, 4)

    def test_add_to_cart_rejects_a_size_not_offered_by_the_product(self):
        unavailable_size = SizeVariant.objects.create(size_name="XL", price=100)

        response = self.client.post(
            reverse("add_to_cart", args=[self.product.slug]),
            {"quantity": "1", "size_variant": str(unavailable_size.uid)},
        )

        self.assertRedirects(
            response,
            reverse("get_product", args=[self.product.slug]),
            fetch_redirect_response=False,
        )
        self.assertFalse(CartItem.objects.filter(profile=self.profile).exists())

    def test_cart_displays_total_and_quantity(self):
        CartItem.objects.create(
            profile=self.profile,
            product=self.product,
            size_variant=self.size,
            quantity=2,
        )

        response = self.client.get(reverse("cart"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Subtotal: $300")
        self.assertContains(response, 'value="2"')

    def test_cart_item_can_be_updated_and_removed(self):
        item = CartItem.objects.create(profile=self.profile, product=self.product)

        response = self.client.post(
            reverse("update_cart_item", args=[item.uid]),
            {"quantity": "3"},
        )
        self.assertRedirects(response, reverse("cart"), fetch_redirect_response=False)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

        response = self.client.post(reverse("remove_cart_item", args=[item.uid]))
        self.assertRedirects(response, reverse("cart"), fetch_redirect_response=False)
        self.assertFalse(CartItem.objects.filter(pk=item.pk).exists())

    def test_invalid_quantity_does_not_add_item(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.product.slug]),
            {"quantity": "0", "size_variant": str(self.size.uid)},
        )

        self.assertRedirects(
            response,
            reverse("get_product", args=[self.product.slug]),
            fetch_redirect_response=False,
        )
        self.assertFalse(CartItem.objects.filter(profile=self.profile).exists())

    def test_cart_requires_authentication(self):
        self.client.logout()

        response = self.client.get(reverse("cart"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('cart')}",
            fetch_redirect_response=False,
        )

    def test_guest_add_to_cart_redirects_to_product_after_login(self):
        self.client.logout()

        response = self.client.post(
            reverse("add_to_cart", args=[self.product.slug]),
            {"quantity": "1", "size_variant": str(self.size.uid)},
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('get_product', args=[self.product.slug])}",
            fetch_redirect_response=False,
        )
