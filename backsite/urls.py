"from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('dashboard/', views.dashboard, name='dashboard'),\n    path('menu/', views.manage_menu, name='manage_menu'),\n]" 
