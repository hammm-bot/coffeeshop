from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Menu, Kategori, RiwayatPemesanan
from django.views.decorators.http import require_POST

# Model tambahan yang kamu harus buat untuk Cart dan CartItem
from .models import Cart, CartItem  # pastikan kamu sudah buat model ini sesuai saran sebelumnya

@login_required
def menu_view(request):
    kategori_id = request.GET.get('kategori')
    kategori_aktif = None
    if kategori_id:
        kategori_aktif = get_object_or_404(Kategori, id=kategori_id)
        menus = Menu.objects.filter(kategori=kategori_aktif)
    else:
        menus = Menu.objects.all()

    kategoris = Kategori.objects.all()
    return render(request, 'menu.html', {
        'menus': menus,
        'kategoris': kategoris,
        'kategori_aktif': kategori_aktif,
    })

@login_required
def pesanan_view(request):
    return render(request, 'pesanan.html')

@login_required
def history_view(request):
    return render(request, 'history.html')

# Helper untuk mendapatkan cart aktif user
def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    return cart

@login_required
@require_POST
def add_to_cart(request, menu_id):
    from django.views.decorators.csrf import csrf_exempt
    import json

    # Terima data JSON dari frontend
    data = json.loads(request.body)
    quantity = int(data.get('quantity', 1))

    menu = get_object_or_404(Menu, id=menu_id)
    cart = get_user_cart(request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, menu=menu)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({'status': 'success', 'message': 'Item added to cart'})

@login_required
def view_cart(request):
    cart = get_user_cart(request.user)
    items = cart.items.select_related('menu').all()

    cart_items = []
    total = 0
    for item in items:
        subtotal = item.menu.harga * item.quantity
        total += subtotal
        cart_items.append({
            'id': item.id,
            'nama': item.menu.nama,
            'quantity': item.quantity,
            'harga': float(item.menu.harga),
            'subtotal': float(subtotal),
        })

    return JsonResponse({'items': cart_items, 'total': total})

@login_required
@require_POST
def update_cart_item(request, item_id):
    import json
    data = json.loads(request.body)
    quantity = int(data.get('quantity', 1))
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if quantity < 1:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return JsonResponse({'status': 'success'})

@login_required
def checkout(request):
    # Implementasikan proses checkout kamu di sini (payment, confirm, dll)
    cart = get_user_cart(request.user)
    cart.is_active = False
    cart.save()
    # Bisa juga buat order baru, kirim email, dsb
    return redirect('menu')  # atau halaman konfirmasi pembayaran

@login_required
def history_view(request):
    history = RiwayatPemesanan.objects.filter(user=request.user).order_by('-tanggal')
    return render(request, 'history.html', {'history': history})