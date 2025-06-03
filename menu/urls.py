from django.urls import path
from .views import menu_view, pesanan_view, history_view

urlpatterns = [
    path('', menu_view, name='menu'),
    path('pesanan/', pesanan_view, name='pesanan'),
    path('history/', history_view, name='history'),
]