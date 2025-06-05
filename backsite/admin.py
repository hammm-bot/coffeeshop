from django.contrib import admin
from .models import Menu, Order, OrderItem

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kategori', 'harga_rupiah')  # ✅ pakai fungsi custom
    search_fields = ('nama',)
    list_filter = ('kategori',)

    @admin.display(description='Harga')  # tampil sebagai "Harga" di tabel admin
    def harga_rupiah(self, obj):
        return f"Rp {obj.harga:,.0f}".replace(",", ".")

# Tampilkan item pesanan di dalam detail Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'metode_pembayaran', 'status', 'created_at')
    list_filter = ('status', 'metode_pembayaran')
    list_editable = ('status',)
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu', 'jumlah', 'subtotal_rupiah')
    list_filter = ('menu',)

    @admin.display(description='Subtotal')
    def subtotal_rupiah(self, obj):
        return f"Rp {obj.menu.harga * obj.jumlah:,.0f}".replace(",", ".")