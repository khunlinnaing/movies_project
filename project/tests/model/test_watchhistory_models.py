from django.test import TestCase
from django.contrib.auth.models import User
from project.models import Movie, Category, WatchHistory  # adjust import path
from django.db.utils import IntegrityError


class WatchHistoryModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="StrongPass123")
        
        # Create a test category
        self.category = Category.objects.create(name="Action")
        
        # Create a test movie
        self.movie = Movie.objects.create(
            title="The Matrix",
            category=self.category,
            release_year=1999,
            duration_minutes=136
        )

    def test_create_watch_history(self):
        """Can create a WatchHistory entry for a user and movie."""
        watch = WatchHistory.objects.create(user=self.user, movie=self.movie, watched_minutes=50)
        self.assertEqual(watch.user, self.user)
        self.assertEqual(watch.movie, self.movie)
        self.assertEqual(watch.watched_minutes, 50)

    def test_unique_together_constraint(self):
        """Cannot create two WatchHistory entries for the same user and movie."""
        WatchHistory.objects.create(user=self.user, movie=self.movie, watched_minutes=30)
        with self.assertRaises(IntegrityError):
            WatchHistory.objects.create(user=self.user, movie=self.movie, watched_minutes=60)

    def test_str_method(self):
        """__str__ method returns 'username watched X min of Movie Title'."""
        watch = WatchHistory.objects.create(user=self.user, movie=self.movie, watched_minutes=75)
        expected = f"{self.user.username} watched 75 min of {self.movie.title}"
        self.assertEqual(str(watch), expected)

    def test_progress_percentage(self):
        """progress_percentage returns correct percentage of movie watched."""
        watch = WatchHistory.objects.create(user=self.user, movie=self.movie, watched_minutes=34)
        expected_percentage = round((34 / 136) * 100, 2)
        self.assertEqual(watch.progress_percentage, expected_percentage)

    def test_progress_percentage_zero_duration(self):
        """If movie duration is 0, progress_percentage should return 0."""
        movie_zero = Movie.objects.create(
            title="Unknown Movie",
            category=self.category,
            release_year=2025,
            duration_minutes=0
        )
        watch = WatchHistory.objects.create(user=self.user, movie=movie_zero, watched_minutes=10)
        self.assertEqual(watch.progress_percentage, 0)
