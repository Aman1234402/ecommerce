from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.shoes = Category.objects.create(category_name="Shoes", slug="shoes")
        self.books = Category.objects.create(category_name="Books", slug="books")
        Product.objects.create(
            product_name="Trail Runner",
            slug="trail-runner",
            category=self.shoes,
            price=80,
            product_description="Lightweight shoes for hiking.",
        )
        Product.objects.create(
            product_name="Python Guide",
            slug="python-guide",
            category=self.books,
            price=30,
            product_description="A practical programming book.",
        )

    def test_search_filters_products_by_name_description_or_category(self):
        response = self.client.get(reverse("index"), {"q": "hiking"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trail Runner")
        self.assertNotContains(response, "Python Guide")

    def test_category_filter_can_be_combined_with_search(self):
        response = self.client.get(
            reverse("index"),
            {"q": "trail", "category": self.shoes.slug},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trail Runner")
        self.assertNotContains(response, "Python Guide")

    def test_search_with_no_matches_shows_empty_state(self):
        response = self.client.get(reverse("index"), {"q": "not-a-real-product"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products found")

    def test_homepage_renders_interactive_catalog_controls(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="product-grid"')
        self.assertContains(response, 'id="catalog-sort"')
        self.assertContains(response, 'data-category-filter="shoes"')
        self.assertContains(response, 'data-favorite-id=')
        self.assertContains(response, "js/storefront.js")
