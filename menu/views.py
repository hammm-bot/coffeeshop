from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from backsite.models import Menu, Order  # ✅ hanya dari backsite
from .models import Kategori, Cart, CartItem, RiwayatPemesanan
import json


import json

from backsite.models import Menu
from .models import Kategori, Cart, CartItem, RiwayatPemesanan

# ─────────────────────────────────────────────────────────────
# ✅ TAMPILKAN MENU
# ─────────────────────────────────────────────────────────────
@login_required
def menu_view(request):
    kategori_id = request.GET.get('kategori')
    kategori_aktif = kategori_id  # kategori_id berupa string: 'coffee', 'non-coffee', dll

    if kategori_id and kategori_id != 'all':
        menus = Menu.objects.filter(kategori=kategori_id)
    else:
        menus = Menu.objects.all()

    return render(request, 'menu.html', {
        'menus': menus,
        'kategori_aktif': kategori_aktif,
    })

# ─────────────────────────────────────────────────────────────
# ✅ HALAMAN PESANAN USER (optional, bisa difungsikan lebih lanjut)
# ─────────────────────────────────────────────────────────────
@login_required
def pesanan_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items', 'items__menu')
    return render(request, 'pesanan.html', {'orders': orders})

# ─────────────────────────────────────────────────────────────
# ✅ HALAMAN RIWAYAT PEMESANAN
# ─────────────────────────────────────────────────────────────
@login_required
def history_view(request):
    history = RiwayatPemesanan.objects.filter(user=request.user).order_by('-tanggal')
    return render(request, 'history.html', {'history': history})


# ─────────────────────────────────────────────────────────────
# ✅ FUNGSI BANTUAN: CART AKTIF USER
# ─────────────────────────────────────────────────────────────
def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user, is_active=True)
    return cart


# ─────────────────────────────────────────────────────────────
# ✅ TAMBAHKAN MENU KE KERANJANG
# ─────────────────────────────────────────────────────────────
@login_required
@require_POST
def add_to_cart(request, menu_id):
    data = json.loads(request.body)
    jumlah = int(data.get('jumlah', 1))

    menu = get_object_or_404(Menu, id=menu_id)
    cart = get_user_cart(request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, menu=menu)
    if not created:
        cart_item.jumlah += jumlah
    else:
        cart_item.jumlah = jumlah
    cart_item.save()

    return JsonResponse({'status': 'success', 'message': 'Item ditambahkan ke keranjang'})


# ─────────────────────────────────────────────────────────────
# ✅ TAMPILKAN ISI KERANJANG
# ─────────────────────────────────────────────────────────────
@login_required
def view_cart(request):
    cart = get_user_cart(request.user)
    items = cart.items.select_related('menu').all()

    cart_items = []
    total = 0
    for item in items:
        subtotal = item.menu.harga * item.jumlah
        total += subtotal
        cart_items.append({
            'id': item.id,
            'nama': item.menu.nama,
            'jumlah': item.jumlah,
            'harga': float(item.menu.harga),
            'subtotal': float(subtotal),
        })

    return JsonResponse({'items': cart_items, 'total': float(total)})


# ─────────────────────────────────────────────────────────────
# ✅ UPDATE JUMLAH ITEM DI KERANJANG
# ─────────────────────────────────────────────────────────────
@login_required
@require_POST
def update_cart_item(request, item_id):
    data = json.loads(request.body)
    jumlah = int(data.get('jumlah', 1))
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if jumlah < 1:
        cart_item.delete()
    else:
        cart_item.jumlah = jumlah
        cart_item.save()

    return JsonResponse({'status': 'success'})


# ─────────────────────────────────────────────────────────────
# ✅ HAPUS ITEM DARI KERANJANG
# ─────────────────────────────────────────────────────────────
@login_required
@require_POST
def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return JsonResponse({'status': 'success'})


# ─────────────────────────────────────────────────────────────
# ✅ PROSES CHECKOUT
# ─────────────────────────────────────────────────────────────
@login_required
def checkout(request):
    cart = get_user_cart(request.user)
    items = cart.items.select_related('menu').all()

    # Simpan sebagai riwayat pemesanan
    for item in items:
        RiwayatPemesanan.objects.create(
            user=request.user,
            nama_produk=item.menu.nama,
            jumlah=item.jumlah,
            total=item.menu.harga * item.jumlah,
        )

    cart.is_active = False
    cart.save()

    return redirect('history')