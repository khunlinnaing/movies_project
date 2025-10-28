from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Info"


# --- Automatically create or update UserInfo when a User is saved ---
@receiver(post_save, sender=User)
def create_or_update_userinfo(sender, instance, created, **kwargs):
    if created:
        UserInfo.objects.create(user=instance)
    else:
        instance.info.save()
        # try:
        # except UserInfo.DoesNotExist:
        #     UserInfo.objects.create(user=instance)



class Category(models.Model):
    """
    Represents a movie genre/category (Action, Comedy, Drama, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Movie(models.Model):
    """
    Movie details: title, duration, genre, description, etc.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='movies')
    description = models.TextField(blank=True)
    release_year = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField(help_text="Total duration of the movie in minutes")
    thumbnail = models.ImageField(upload_to='movies/thumbnails/', blank=True, null=True)
    video_file = models.FileField(upload_to='movies/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class WatchHistory(models.Model):
    """
    Tracks how many minutes each user has watched of a movie.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watch_history')
    watched_minutes = models.PositiveIntegerField(default=0)
    last_watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')
        verbose_name_plural = "Watch History"

    def __str__(self):
        return f"{self.user.username} watched {self.watched_minutes} min of {self.movie.title}"

    @property
    def progress_percentage(self):
        """
        Returns how much of the movie the user has watched, as a percentage.
        """
        if self.movie.duration_minutes > 0:
            return round((self.watched_minutes / self.movie.duration_minutes) * 100, 2)
        return 0

