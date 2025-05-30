from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.login, name='login'),  
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('detail/', views.detail, name='detail'),
]