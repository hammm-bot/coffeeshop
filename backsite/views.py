from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.utils.timezone import now
from .models import Order
from django.db.models.functions import TruncMonth
import csv
from django.http import HttpResponse

# Cek apakah user adalah admin/staff
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    today = now().date()
    month = now().month

    total_hari_ini = Order.objects.filter(created_at__date=today).count()
    total_bulan_ini = Order.objects.filter(created_at__month=month).count()
    total_transaksi = Order.objects.count()

    # Ambil data penjualan per bulan (6 bulan terakhir)
    monthly_data = (
        Order.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(jumlah=Count('id'))
        .order_by('month')
    )

    labels = [data['month'].strftime('%B') for data in monthly_data]
    values = [data['jumlah'] for data in monthly_data]

    context = {
        'total_hari_ini': total_hari_ini,
        'total_bulan_ini': total_bulan_ini,
        'total_transaksi': total_transaksi,
        'labels': labels,
        'values': values,
    }

    return render(request, 'backsite/dashboard.html', context)

def export_transaksi_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="laporan_transaksi.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Order', 'User', 'Tanggal', 'Status', 'Metode Pembayaran'])

    for order in Order.objects.all():
        writer.writerow([order.id, order.user.username, order.created_at.strftime('%Y-%m-%d'), order.status, order.metode_pembayaran])

    return response