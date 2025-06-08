from django.contrib import admin
from .models import Menu

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kategori', 'harga_rupiah')  # ✅ pakai fungsi custom
    search_fields = ('nama',)
    list_filter = ('kategori',)

    @admin.display(description='Harga')  # tampil sebagai "Harga" di tabel admin
    def harga_rupiah(self, obj):
        return f"Rp {obj.harga:,.0f}".replace(",", ".")