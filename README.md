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

<br>
<br>
<br>
<br>

## FITUR SCRIPT:
### ✅ Hanya login jika diperlukan:

1. Cek captive portal - hanya login jika ada portal Ruijie di `http://www.msftconnecttest.com/redirect`
2. CukuP 1 User saja yang login jika ada Captive Portal Ruijie. jika ada berhasil maka user lain tidak perlu login di Captive Portal
3. Tidak mengubah MAC address OpenWRT

### ✅ Multi-credentials:

1. Melakukan percobaan login user pertama
2. Jika gagal, coba dengan user ke dua dan seterusnya

### ✅ Smart monitoring:

1. bisa dengan Crontab Monitor koneksi internet setiap 5 menit.
2. Otomatis login jika internet mati dan ada captive portal.
3. Logging detail untuk debugging

### ✅ Aman:

1. Tidak mengubah konfigurasi jaringan.
2. Restore state jika gagal.
3. Handle error dengan baik


### Topologi Jaringan
```
[INTERNET]
    |
[Ruijie Access Point]
    | Mode: Captive Portal/Hotspot
    | Jarak: 100M
    | WiFi: SSID_Hotspot_Ruijie
    |
[Tenda O3V2]
    | Mode: Client (WiFi to Ethernet Bridge)
    | Antena: Menangkap sinyal dari Ruijie
    | Port: eth2 → LAN cable
    |
[OpenWRT Router]
    | Fungsi: Router utama & DHCP Server
    | Port WAN: Terhubung ke Tenda O3V2
    | Firewall & NAT: SCRIPT Diatur di sini
    |
[Tenda AC1200]
    | Mode: Access Point (AP)
    | Terhubung via LAN ke OpenWRT
    | WiFi: SSID_Lokal (disediakan ke user)
```

### Diagram Proses Script
```
            [INTERNET]
                |
                │
                ▼                                      
           [Ruijie AP] ─────────┐          
           (SSID_Hotspot)       │
           [DHCP:192.168.100.1/24]                  
                │          [Jarak 100M]                     
                │           [Wireless]                  
         [Captive Portal]◄──────┘
                │
                │
                ▼               
           [Tenda O3V2]─→────────[Captive Portal]───────┐
           Mode: Client                                 ▼
                │                                       │
                │ eth2 (LAN Cable)                      │
                ▼ DHCP:192.168.100.0/24                 │
          ----------------------                        ▼
          | [OpenWRT Router]    |◄─[Captive Portal]◄────┘
          | LAN: 192.168.1.1/24 |                       
          ----------------------                        
                ▼                                       
          [LAN] │                                       
                └───────→ [SCRIPT AUTO LOGIN Captive Portal]         
                                   ▼         
                            [SUKSES LOGIN]─────────→[GAGAL]         
                                   ▼                   ▼
                                   │                   │
                                   │                   │
┌──────────────────────→[BYPASS Captive Portal]        │
│                                  │                   │
│           [LAN]┌─────────────────┘                   │
↑                ▼                                     │
│           [Tenda AC1200]                             │         
│           Mode: AP                                   │
│           DHCP:192.168.1.0/24                        │
↑                │                                     │         
│          ┌─────┼─────┐                               │         
│          │     │     │                               │         
│        [User1][User2][User3]                         │         
↑          │     │     │                               │         
│      [Auth via Captive Portal]◄──────────────────────┘
│          │     │     │
↑          └────→┼◄────┘
│                │
│                ▼
└────────◄─[SUKSES LOGIN]
```


### Install script:
```
mkdir /www/auto-Ruijie
cd /www/auto-Ruijie

# Simpan script
echo '[konten auto_ruijie_smart.py di atas]' > auto_ruijie_smart.py
echo '[konten monitor_ruijie.py di atas]' > monitor_ruijie.py <<<<<< OPSIONAL, menggunakan Crontab bisa saja

# Beri permission
chmod +x auto_ruijie_smart.py monitor_ruijie.py

# Install requests jika belum
pip3 install requests
```

### Test script:
```
# Test smart login (hanya login jika diperlukan)
python3 auto_ruijie_smart.py

# Test monitor (check setiap 60 detik)
python3 monitor_ruijie.py
```
