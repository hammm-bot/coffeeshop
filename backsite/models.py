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

class Order(models.Model):
    STATUS_CHOICES = [
        ('diproses', 'Diproses'),
        ('dikirim', 'Dikirim'),
        ('selesai', 'Selesai'),
    ]
    METODE_CHOICES = [
        ('COD', 'COD'),
        ('E-Wallet', 'E-Wallet'),
        ('Transfer', 'Transfer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metode_pembayaran = models.CharField(max_length=20, choices=METODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='diproses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu.nama} x {self.quantity}"
