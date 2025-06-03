from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def menu_view(request):
    return render(request, 'menu/menu.html')

@login_required
def pesanan_view(request):
    return render(request, 'menu/pesanan.html')

@login_required
def history_view(request):
    return render(request, 'menu/history.html')