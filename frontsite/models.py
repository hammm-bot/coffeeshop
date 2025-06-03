from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"Profil {self.user.username}"