from django.test import TestCase
from django.utils.text import slugify
from project.models import Category  # Adjust import path to match your app


class CategoryModelTest(TestCase):
    def test_create_category_auto_slug(self):
        """
        Saving a category without a slug should auto-generate one from the name.
        """
        category = Category.objects.create(name="Action")
        self.assertEqual(category.slug, slugify("Action"))
        self.assertEqual(str(category), "Action")

    def test_create_category_with_custom_slug(self):
        """
        If a slug is provided manually, it should not be overwritten.
        """
        category = Category.objects.create(name="Comedy", slug="funny-movies")
        self.assertEqual(category.slug, "funny-movies")

    def test_category_name_unique(self):
        """
        Name field must be unique.
        """
        Category.objects.create(name="Drama")
        with self.assertRaises(Exception):
            # Should raise IntegrityError
            Category.objects.create(name="Drama")

    def test_category_slug_unique(self):
        """
        Slug field must be unique.
        """
        Category.objects.create(name="Thriller", slug="thriller")
        with self.assertRaises(Exception):
            Category.objects.create(name="Suspense", slug="thriller")

    def test_str_method_returns_name(self):
        """
        __str__() should return the category name.
        """
        category = Category.objects.create(name="Horror")
        self.assertEqual(str(category), "Horror")
