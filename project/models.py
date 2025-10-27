from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Info"


# --- Automatically create or update UserInfo when a User is saved ---
@receiver(post_save, sender=User)
def create_or_update_user_info(sender, instance, created, **kwargs):
    if created:
        UserInfo.objects.create(user=instance)
    else:
        instance.info.save()
