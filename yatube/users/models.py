from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, null=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    description = models.TextField(blank=True)
    