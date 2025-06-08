from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from backsite.models import Menu
from .models import Kategori, Cart, CartItem, RiwayatPemesanan
from django.db.models import Sum
from .models import PesananAktif
from django.shortcuts import render, redirect
from .models import TransaksiManual
from .forms import BuktiPembayaranForm
from .models import Cart, CartItem, TransaksiManual
from django.db.models import F, Sum
from django.shortcuts import render, redirect
from django.utils import timezone
import json
from django.views.decorators.csrf import csrf_exempt

import json

from backsite.models import Menu
from .models import Kategori, Cart, CartItem, RiwayatPemesanan
from django.views.decorators.http import require_POST
from .forms import BuktiPembayaranForm

# ─────────────────────────────────────────────────────────────
# ✅ TAMPILKAN MENU
# ─────────────────────────────────────────────────────────────

@login_required
def menu_view(request):
    menus = Menu.objects.all()
    cart = get_user_cart(request.user)
    cart_items = cart.items.select_related('menu').all()
    total = sum(item.menu.harga * item.jumlah for item in cart_items)
    total_item = cart.items.aggregate(total=Sum('jumlah'))['total'] or 0

    context = {
        'menus': menus,
        'kategori_list': ["coffee", "non-coffee", "snack"],
        'cart_items': cart_items,
        'total': total,
        'total_item': total_item,
    }
    return render(request, 'menu.html', context)
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
    cart = Cart.objects.filter(user=user, is_active=True).order_by('-id').first()
    if not cart:
        cart = Cart.objects.create(user=user, is_active=True)
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
from .forms import BuktiPembayaranForm

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = get_user_cart(request.user)
        items = cart.items.select_related('menu').all()

        if not items.exists():
            return JsonResponse({'status': 'error', 'message': 'Keranjang kosong.'})

        total = sum(item.menu.harga * item.jumlah for item in items)

        html_qrcode_form = render_to_string('partial_qrcode_form.html', {
            'total': total
        }, request=request)

        return JsonResponse({'status': 'success', 'html_qrcode_form': html_qrcode_form})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'})
    
def create_pesanan_aktif_from_cart(user):
    cart = Cart.objects.filter(user=user, is_active=True).first()
    if not cart:
        return
    items = cart.items.select_related('menu').all()
    for item in items:
        PesananAktif.objects.create(
            user=user,
            menu=item.menu,
            jumlah=item.jumlah,
            status='menunggu',
            tanggal=timezone.now(),
        )
    # Tandai cart sudah tidak aktif dan hapus item cart
    cart.is_active = False
    cart.save()
    items.delete()
    
@require_POST
@login_required
def confirm_payment(request):
    user = request.user

    try:
        # Ambil transaksi terakhir milik user
        transaksi = TransaksiManual.objects.filter(user=user).latest('created_at')
    except TransaksiManual.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Transaksi tidak ditemukan'})

    # ✅ Validasi wajib: Pastikan sudah upload bukti pembayaran
    if not transaksi.bukti_pembayaran:
        return JsonResponse({'status': 'error', 'message': 'Harap upload bukti pembayaran terlebih dahulu'})

    # ✅ Tandai transaksi diproses
    transaksi.status = 'diproses'
    transaksi.save()

    # ✅ Buat pesanan dari cart (jika belum pernah dibuat)
    cart = Cart.objects.filter(user=user, is_active=True).first()
    if cart:
        items = cart.items.select_related('menu').all()
        for item in items:
            PesananAktif.objects.create(
                user=user,
                menu=item.menu,
                jumlah=item.jumlah,
                status='menunggu',
                tanggal=timezone.now()
            )
        # Tandai cart tidak aktif & bersihkan
        cart.is_active = False
        cart.save()
        items.delete()

    return JsonResponse({'status': 'success'})

@require_POST
@login_required
@csrf_exempt
def upload_bukti(request):
    if not request.FILES.get('bukti_pembayaran'):
        return JsonResponse({'status': 'error', 'message': 'File tidak ditemukan'})

    cart = get_user_cart(request.user)
    items = cart.items.select_related('menu').all()

    if not items.exists():
        return JsonResponse({'status': 'error', 'message': 'Keranjang kosong.'})

    total = sum(item.menu.harga * item.jumlah for item in items)

    # Simpan transaksi manual
    transaksi = TransaksiManual.objects.create(
        user=request.user,
        total=total,
        status='verifikasi',
        bukti_pembayaran=request.FILES['bukti_pembayaran']
    )

    # Simpan item ke PesananAktif
    for item in items:
        PesananAktif.objects.create(
            user=request.user,
            menu=item.menu,
            jumlah=item.jumlah,
            status='menunggu',  # atau status default kamu
        )

    # Kosongkan cart
    cart.items.all().delete()

    return JsonResponse({'status': 'success'})