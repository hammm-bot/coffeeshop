from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Menu(models.Model):
    KATEGORI_CHOICES = [
        ('coffee', 'Coffee'),
        ('non-coffee', 'Non-Coffee'),
        ('snack', 'Snack'),
    ]
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()
    harga = models.DecimalField(max_digits=8, decimal_places=2)
    gambar = models.ImageField(upload_to='menu/')
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)

    def __str__(self):
        return self.nama