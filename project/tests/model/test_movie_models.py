from django.test import TestCase
from django.utils.text import slugify
from project.models import Movie, Category  # adjust import path to match your project


class MovieModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Action")

    def test_auto_slug_created_on_save(self):
        """
        When a movie is saved without a slug, it should automatically generate one from the title.
        """
        movie = Movie.objects.create(
            title="The Great Escape",
            category=self.category,
            release_year=1963,
            duration_minutes=120,
        )
        self.assertEqual(movie.slug, slugify("The Great Escape"))
        self.assertEqual(str(movie), "The Great Escape (1963)")

    def test_custom_slug_is_not_overwritten(self):
        """
        If a custom slug is provided, it should not be replaced by slugify(title).
        """
        movie = Movie.objects.create(
            title="Inception",
            slug="dream-movie",
            category=self.category,
            release_year=2010,
            duration_minutes=148,
        )
        self.assertEqual(movie.slug, "dream-movie")

    def test_slug_is_unique(self):
        """
        The slug field must be unique.
        """
        Movie.objects.create(
            title="Interstellar",
            slug="interstellar",
            category=self.category,
            release_year=2014,
            duration_minutes=169,
        )
        with self.assertRaises(Exception):
            Movie.objects.create(
                title="Another Space Movie",
                slug="interstellar",  # duplicate slug
                category=self.category,
                release_year=2020,
                duration_minutes=100,
            )

    def test_movie_can_have_blank_optional_fields(self):
        """
        Optional fields (description, thumbnail, video_file) can be blank or null.
        """
        movie = Movie.objects.create(
            title="No Media Movie",
            category=self.category,
            release_year=2025,
            duration_minutes=95,
        )

        # Description is blank string
        self.assertEqual(movie.description, "")

        # Thumbnail and video_file are empty
        self.assertFalse(movie.thumbnail)  # evaluates to False if no file is uploaded
        self.assertFalse(movie.video_file)  # same here


    def test_foreign_key_relationship(self):
        """
        Each movie should be linked to a category correctly.
        """
        movie = Movie.objects.create(
            title="Mad Max",
            category=self.category,
            release_year=1979,
            duration_minutes=110,
        )
        self.assertEqual(movie.category, self.category)
        self.assertIn(movie, self.category.movies.all())

    def test_str_method_returns_title_and_year(self):
        """
        The __str__ method should return 'Title (Year)' format.
        """
        movie = Movie.objects.create(
            title="The Matrix",
            category=self.category,
            release_year=1999,
            duration_minutes=136,
        )
        self.assertEqual(str(movie), "The Matrix (1999)")
