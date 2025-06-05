from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User 
from backsite.models import Menu

class Kategori(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    jumlah = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.menu.harga * self.jumlah

class RiwayatPemesanan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_produk = models.CharField(max_length=100)
    jumlah = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)  # <- disarankan ditambahkan
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama_produk} ({self.jumlah}) - {self.user.username}"