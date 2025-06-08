from django.contrib import admin
from .models import Kategori, Cart, CartItem, RiwayatPemesanan, PesananAktif, TransaksiManual
from backsite.models import Menu
from django.utils.html import format_html

def rupiah_format(value):
    return format_html("Rp {:,}".format(value).replace(",", "."))

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
    list_display = ['id', 'user', 'nama_produk', 'jumlah', 'rupiah_total', 'tanggal']
    list_filter = ['tanggal']
    search_fields = ['user__username', 'nama_produk']

    def rupiah_total(self, obj):
        return rupiah_format(obj.total)
    rupiah_total.short_description = 'Total'

@admin.register(PesananAktif)
class PesananAktifAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'menu', 'jumlah', 'rupiah_harga', 'rupiah_total', 'status', 'tanggal']
    list_editable = ['status']
    list_filter = ['status', 'tanggal']
    search_fields = ['user__username', 'menu__nama']

    def rupiah_harga(self, obj):
        return rupiah_format(obj.harga)
    rupiah_harga.short_description = 'Harga'

    def rupiah_total(self, obj):
        return rupiah_format(obj.total)
    rupiah_total.short_description = 'Total'

@admin.register(TransaksiManual)
class TransaksiManualAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'rupiah_total', 'status', 'created_at']
    readonly_fields = ['preview_bukti']
    fields = ['user', 'total', 'status', 'bukti_pembayaran', 'preview_bukti']

    def rupiah_total(self, obj):
        return rupiah_format(obj.total)
    rupiah_total.short_description = 'Total'

    def preview_bukti(self, obj):
        if obj.bukti_pembayaran:
            return format_html('<img src="{}" style="max-height: 300px;" />', obj.bukti_pembayaran.url)
        return "Belum ada bukti"