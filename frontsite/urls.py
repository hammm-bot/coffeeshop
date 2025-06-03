from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.login_view, name='login'),  
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('setting/', views.profile_setting, name='profile_setting'),
    path('setting/update/', views.update_profile, name='update_profile'),
]