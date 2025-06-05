"from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('dashboard/', views.dashboard, name='dashboard'),\n    path('menu/', views.manage_menu, name='manage_menu'),\n]" 

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import dashboard_view
from .views import export_transaksi_csv

urlpatterns = [
    path('dashboard/', dashboard_view, name='admin-dashboard'),
    path('export-transaksi/', export_transaksi_csv, name='export-transaksi'),
    # ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)