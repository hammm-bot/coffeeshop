from django.contrib import admin
from .models import Kategori, Cart, CartItem, RiwayatPemesanan, PesananAktif
from .models import TransaksiManual
from backsite.models import Menu
from django.utils.html import format_html

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ['id', 'nama']
    search_fields = ['nama']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__username']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'menu', 'jumlah']
    search_fields = ['cart__user__username', 'menu__nama']

@admin.register(RiwayatPemesanan)
class RiwayatPemesananAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'nama_produk', 'jumlah', 'total', 'tanggal']
    list_filter = ['tanggal']
    search_fields = ['user__username', 'nama_produk']

@admin.register(PesananAktif)
class PesananAktifAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'menu', 'jumlah', 'harga', 'total', 'status', 'tanggal']
    list_editable = ['status']  # Bisa edit langsung di list view
    list_filter = ['status', 'tanggal']
    search_fields = ['user__username', 'menu__nama']

@admin.register(TransaksiManual)
class TransaksiManualAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at']
    readonly_fields = ['preview_bukti', 'created_at']
    fields = ['user', 'total', 'status', 'bukti_pembayaran', 'preview_bukti']

    def preview_bukti(self, obj):
        if obj.bukti_pembayaran:
            return format_html('<img src="{}" style="max-height: 300px;" />', obj.bukti_pembayaran.url)
        return "Tidak ada bukti"

    preview_bukti.short_description = "Preview Bukti Pembayaran"