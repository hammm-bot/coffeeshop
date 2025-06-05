from django.contrib import admin

from django.contrib import admin
from .models import Menu, Order, OrderItem

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kategori', 'harga')
    search_fields = ('nama',)
    list_filter = ('kategori',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'metode_pembayaran', 'status', 'created_at')
    list_filter = ('status', 'metode_pembayaran')
    inlines = [OrderItemInline]
