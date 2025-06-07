import mysql.connector
import random
from datetime import datetime, timedelta

# Koneksi ke database
db = mysql.connector.connect(
    host="localhost",
    user="root",        # sesuaikan
    password="",        # sesuaikan
    database="coffeeshop"
)

cursor = db.cursor()

metode_list = ['cash', 'qris', 'debit', 'E-Wallet']
status_list = ['pending', 'diproses', 'success']

# Total 12 bulan, target rata-rata ~8-9 transaksi/bulan
jumlah_per_bulan = [8, 9, 8, 8, 9, 8, 8, 9, 8, 8, 9, 8]  # Total = 100

for bulan in range(1, 13):
    for _ in range(jumlah_per_bulan[bulan - 1]):
        metode = random.choice(metode_list)
        status = random.choice(status_list)

        # Tanggal aman (1-28)
        hari = random.randint(1, 28)
        jam = random.randint(7, 22)
        menit = random.randint(0, 59)
        detik = random.randint(0, 59)

        created_at = datetime(2025, bulan, hari, jam, menit, detik).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO backsite_order (metode_pembayaran, status, created_at, user_id)
            VALUES (%s, %s, %s, %s)
        """, (metode, status, created_at, 2))

db.commit()
print("✅ 100 data dummy seimbang per bulan berhasil diinsert.")
cursor.close()
db.close()