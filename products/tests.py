from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product, ProductImage, SizeVariant


class ProductViewTests(TestCase):
    def test_product_detail_renders_product(self):
        category = Category.objects.create(category_name='Shoes', slug='shoes')
        product = Product.objects.create(
            product_name='Off-White Odsy-1000 Low-Top Sneakers',
            slug='demo-product',
            category=category,
            price=815,
            product_description='Sneakers product details.',
        )
        response = self.client.get(
            reverse('get_product', args=[product.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Off-White Odsy-1000 Low-Top Sneakers')
        self.assertContains(response, 'Sneakers product details.')

    def test_product_detail_updates_price_for_selected_size(self):
        category = Category.objects.create(category_name="Clothing", slug="clothing")
        product = Product.objects.create(
            product_name="Everyday Hoodie",
            slug="everyday-hoodie",
            category=category,
            price=100,
            product_description="A warm everyday hoodie.",
        )
        size = SizeVariant.objects.create(size_name="L", price=25)
        product.size_variant.add(size)

        response = self.client.get(
            reverse("get_product", args=[product.slug]),
            {"size": str(size.uid)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "125")
        self.assertContains(response, 'data-base-price="100"')
        self.assertContains(response, 'data-size-price="25"')
        self.assertContains(response, f'value="{size.uid}" data-size-price="25" checked')

    def test_product_gallery_displays_all_uploaded_product_images(self):
        category = Category.objects.create(category_name="Clothing", slug="clothing")
        product = Product.objects.create(
            product_name="Classic Jeans",
            slug="classic-jeans",
            category=category,
            price=100,
            product_description="Classic denim jeans.",
        )
        ProductImage.objects.create(product=product, image="product/front.jpg")
        ProductImage.objects.create(product=product, image="product/back.jpg")

        response = self.client.get(reverse("get_product", args=[product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-image-url="/media/product/front.jpg"')
        self.assertContains(response, 'data-image-url="/media/product/back.jpg"')
        self.assertContains(response, 'id="gallery-next"')
        self.assertContains(response, 'id="open-image-viewer"')
