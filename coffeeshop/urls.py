from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static  # ⬅️ Tambahkan ini

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontsite.urls')),
    path('menu/', include('menu.urls')),
]

# ✅ Tambahkan ini agar file media (seperti foto) bisa dilayani saat development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)