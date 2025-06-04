from django.db import models
from django.contrib.auth.models import User

class Menu(models.Model):
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField(blank=True)
    harga = models.DecimalField(max_digits=6, decimal_places=2)
    gambar = models.ImageField(upload_to='menu/', blank=True)
    kategori = models.ForeignKey('Kategori', on_delete=models.CASCADE, related_name='menus', null=True, blank=True)

    def __str__(self):
        return self.nama

class Kategori(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)  # menandai cart aktif atau sudah selesai

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def subtotal(self):
        return self.menu.harga * self.quantity
    
class RiwayatPemesanan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_produk = models.CharField(max_length=100)
    jumlah = models.PositiveIntegerField()
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama_produk} ({self.jumlah}) - {self.user.username}"