<div align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/9/92/Openwrt_Logo.svg" alt="OpenWrt - Bluetooth Audio di OpenWrt" width="200"/>
<br>
<img src="https://upload.wikimedia.org/wikipedia/commons/b/bf/Armbianlogo.png" alt="OpenWrt - Bluetooth Audio di Armbian" width="200"/>

![License](https://img.shields.io/github/license/fahrulariza/ruijie-auto-login-portal-openwrt)
[![GitHub All Releases](https://img.shields.io/github/downloads/fahrulariza/ruijie-auto-login-portal-openwrt/total)](https://github.com/fahrulariza/ruijie-auto-login-portal-openwrt/releases)
![Total Commits](https://img.shields.io/github/commit-activity/t/fahrulariza/ruijie-auto-login-portal-openwrt)
![Top Language](https://img.shields.io/github/languages/top/fahrulariza/ruijie-auto-login-portal-openwrt)
[![Open Issues](https://img.shields.io/github/issues/fahrulariza/ruijie-auto-login-portal-openwrt)](https://github.com/fahrulariza/ruijie-auto-login-portal-openwrt/issues)

<h1>Ruijie Auto Login Captive Portal Script OpenWRT</h1>
<p>Kelola router berbasis OS OpenWrt dan Armbian Linux dengan mudah dan kreatif!</p>
</div>

## FITUR SCRIPT INTELEGEN:
### ✅ Hanya login jika diperlukan:

1. pengecekan internet
2. Cek captive portal - hanya login jika ada portal Ruijie
3. Tidak mengubah MAC address - karena terbukti merusak koneksi

### ✅ Multi-credentials:

1. Melakukan percobaan login user pertama
2. Jika gagal, coba dengan user ke dua

### ✅ Smart monitoring:

1. bisa dengan Crontab Monitor koneksi internet setiap 5 menit.
2. Otomatis login jika internet mati dan ada captive portal.
3. Logging detail untuk debugging

### ✅ Aman:

1. Tidak mengubah konfigurasi jaringan.
2. Restore state jika gagal.
3. Handle error dengan baik
