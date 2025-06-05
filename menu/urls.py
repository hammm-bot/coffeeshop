from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('pesanan/', views.pesanan_view, name='pesanan'),
    path('history/', views.history_view, name='history'),

    path('add-to-cart/<int:menu_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/delete/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
]