from django.db import models
from django.contrib.auth.models import User
from backsite.models import Menu
from io import BytesIO
from django.core.files.base import ContentFile
import qrcode

class Kategori(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart {self.id} - {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    jumlah = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.menu.harga * self.jumlah

    def __str__(self):
        return f"{self.menu.nama} x {self.jumlah}"

class RiwayatPemesanan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_produk = models.CharField(max_length=100)
    jumlah = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama_produk} ({self.jumlah}) - {self.user.username}"

class PesananAktif(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu Konfirmasi'),
        ('diproses', 'Diproses'),
        ('siap', 'Siap di Pickup'),
        ('selesai', 'Selesai'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True)
    jumlah = models.PositiveIntegerField()
    harga = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tanggal = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ambil versi lama sebelum disimpan (untuk deteksi perubahan status)
        if self.pk:
            previous = PesananAktif.objects.get(pk=self.pk)
        else:
            previous = None

        # Hitung ulang total
        if self.menu:
            self.harga = self.menu.harga
            self.total = self.harga * self.jumlah

        super().save(*args, **kwargs)

        # Jika status berganti ke selesai, pindah ke riwayat
        if self.status == 'selesai':
            if not previous or previous.status != 'selesai':
                RiwayatPemesanan.objects.create(
                    user=self.user,
                    nama_produk=self.menu.nama if self.menu else 'Tanpa Nama',
                    jumlah=self.jumlah,
                    total=self.total,
                )
                self.delete()

    def __str__(self):
        return f"{self.menu.nama if self.menu else 'Tanpa Menu'} ({self.status}) - {self.user.username}"

class TransaksiManual(models.Model):
    STATUS_CHOICES = [
        ('verifikasi', 'Menunggu Verifikasi'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bukti_pembayaran = models.ImageField(upload_to='bukti_pembayaran/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from .models import Cart, CartItem, PesananAktif  # hindari circular import

        is_newly_approved = False
        if self.pk:
            old = TransaksiManual.objects.get(pk=self.pk)
            if old.status != 'disetujui' and self.status == 'disetujui':
                is_newly_approved = True

        super().save(*args, **kwargs)

        if is_newly_approved:
            cart = Cart.objects.filter(user=self.user, is_active=True).first()
            if cart:
                for item in cart.items.all():
                    PesananAktif.objects.create(
                        user=self.user,
                        menu=item.menu,
                        jumlah=item.jumlah,
                        harga=item.menu.harga,
                        total=item.menu.harga * item.jumlah,
                        status='aktif'
                    )
                cart.is_active = False
                cart.save()