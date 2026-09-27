from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    telegram_id = models.CharField(max_length=120)
    github_url = models.URLField()
    bio = models.TextField(max_length=500)
    is_free = models.BooleanField(default = True)
    is_verified = models.BooleanField(default = False)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
