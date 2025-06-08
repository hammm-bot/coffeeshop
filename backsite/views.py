from menu.models import PesananAktif

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
import csv

from menu.models import PesananAktif  # Ganti dengan model baru

# Cek apakah user adalah admin/staff
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    today = now().date()
    month = now().month

    total_hari_ini = PesananAktif.objects.filter(tanggal__date=today).count()
    total_bulan_ini = PesananAktif.objects.filter(tanggal__month=month).count()
    total_transaksi = PesananAktif.objects.count()

    # Ambil data penjualan per bulan (6 bulan terakhir)
    monthly_data = (
        PesananAktif.objects.annotate(month=TruncMonth('tanggal'))
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

@login_required
@user_passes_test(is_admin)
def export_transaksi_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="laporan_transaksi.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Pesanan', 'User', 'Menu', 'Tanggal', 'Status', 'Total'])

    for pesanan in PesananAktif.objects.all():
        writer.writerow([
            pesanan.id,
            pesanan.user.username,
            pesanan.menu.nama if pesanan.menu else '–',
            pesanan.tanggal.strftime('%Y-%m-%d'),
            pesanan.get_status_display(),
            f"{pesanan.total:.2f}",
        ])

    return response
