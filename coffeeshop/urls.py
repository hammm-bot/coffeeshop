from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static  # ⬅️ Tambahkan ini
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    
    # ⬇️ Tambahkan ini agar bisa akses dashboard custom dari /admin/backsite/
    path('admin/backsite/', include('backsite.urls')),
    
    # Akses admin default
    path('admin/', admin.site.urls),


    # Opsional: Redirect langsung /admin/ ke /admin/backsite/dashboard/
    path('admin/', lambda request: redirect('/admin/backsite/dashboard/')),

    # Akses frontend dan menu
    path('', include('frontsite.urls')),
    path('menu/', include('menu.urls')),
    path('backsite/', include('backsite.urls')),  # tetap aktif kalau mau akses dari sini juga
]

# ✅ Tambahkan ini agar file media (seperti foto) bisa dilayani saat development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)