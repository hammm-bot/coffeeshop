from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from backsite.models import Menu
from .models import Kategori, Cart, CartItem, RiwayatPemesanan
from django.db.models import Sum
from .models import PesananAktif
from django.shortcuts import render, redirect
from .models import TransaksiManual
from .forms import BuktiPembayaranForm
from .models import Cart, CartItem, TransaksiManual
from .forms import BuktiPembayaranForm
from django.db.models import F, Sum
from django.shortcuts import render, redirect
import json


import json

from backsite.models import Menu
from .models import Kategori, Cart, CartItem, RiwayatPemesanan

# ─────────────────────────────────────────────────────────────
# ✅ TAMPILKAN MENU
# ─────────────────────────────────────────────────────────────

def menu_view(request):
    menus = Menu.objects.all()
    cart = get_user_cart(request.user)
    cart_items = cart.items.select_related('menu').all()
    total = sum(item.menu.harga * item.jumlah for item in cart_items)
    total_item = cart.items.aggregate(total=Sum('jumlah'))['total'] or 0

    kategori_list = ["coffee", "non-coffee", "snack"]

    return render(request, 'menu.html', {
        'menus': menus,
        'kategori_list': kategori_list,
        'cart_items': cart_items,
        'total': total,
        'total_item': total_item,
    })

# ─────────────────────────────────────────────────────────────
# ✅ HALAMAN PESANAN USER (optional, bisa difungsikan lebih lanjut)
# ─────────────────────────────────────────────────────────────
@login_required
def pesanan_view(request):
    orders = PesananAktif.objects.filter(user=request.user).exclude(status='selesai').order_by('-tanggal').select_related('menu')
    
    transaksi = TransaksiManual.objects.filter(user=request.user).order_by('-created_at').first()

    for o in orders:
        print(f"ID: {o.id} | Menu: {o.menu} | Nama: {o.menu.nama if o.menu else 'None'}")

    total_harga = orders.aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'pesanan.html', {
        'orders': orders,
        'total_harga': total_harga
    })

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

    total_item = cart.items.aggregate(total=Sum('jumlah'))['total'] or 0

    return JsonResponse({
        'items': cart_items,
        'total': float(total),
        'total_item': total_item 
    })

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

    for item in items:
        PesananAktif.objects.create(
            user=request.user,
            menu=item.menu,  # Tambahkan ini agar relasi menu terisi
            jumlah=item.jumlah,
            harga=item.menu.harga,
            total=item.menu.harga * item.jumlah,
            status='proses'
        )

    cart.items.all().delete()
    cart.is_active = False
    cart.save()

    return redirect('pesanan')


def checkout_view(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    
    # Jika cart kosong
    if not cart or not cart.items.exists():
        return render(request, 'pesanan.html', {
            'orders': [],
            'total_harga': 0,
            'transaksi': None,
            'form': None
        })

    # Hitung total dari cart
    total = cart.items.aggregate(
        total=Sum(F('menu__harga') * F('jumlah'))
    )['total'] or 0

    # Buat transaksi baru atau ambil yang pending
    transaksi, created = TransaksiManual.objects.get_or_create(
        user=request.user,
        status='pending',
        defaults={'total': total}
    )

    # Update total jika cart berubah
    if not created:
        transaksi.total = total
        transaksi.save()

    # Form upload
    if request.method == 'POST':
        form = BuktiPembayaranForm(request.POST, request.FILES, instance=transaksi)
        if form.is_valid():
            transaksi.status = 'verifikasi'
            form.save()
            return redirect('menu:pesanan')
    else:
        form = BuktiPembayaranForm(instance=transaksi)

    return render(request, 'pesanan.html', {
        'orders': [],  # jika belum generate PesananAktif
        'total_harga': 0,
        'transaksi': transaksi,
        'form': form
    })