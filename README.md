# Ruijie Auto Login Captive Portal Script OpenWRT


## FITUR SCRIPT INTELEGEN:
### ✅ Hanya login jika diperlukan:

1. pengecekan internet
2. Cek captive portal - hanya login jika ada portal Ruijie
3. Tidak mengubah MAC address - karena terbukti merusak koneksi

### ✅ Multi-credentials:

1. Coba login dengan Umum:PKMUMUM1 dulu
2. Jika gagal, coba dengan Admin:PKMADMIN1

### ✅ Smart monitoring:

1. Monitor koneksi internet setiap 5 menit.
2. Otomatis login jika internet mati dan ada captive portal.
3. Logging detail untuk debugging

### ✅ Aman:

1. Tidak mengubah konfigurasi jaringan.
2. Restore state jika gagal.
3. Handle error dengan baik
