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

1. `Deteksi kondisi`: Script mendeteksi internet mati + captive portal aktif di `http://www.msftconnecttest.com/redirect`
2. Cukup 1 User saja yang login jika ada Captive Portal Ruijie. jika ada berhasil maka user lain tidak perlu login di Captive Portal
3. BYPASS Captive Portal jika sudah ada user yang berhasil login di Captive Portal

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
4. Tidak mengubah MAC address OpenWRT

## Topologi Jaringan
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

1. `Deteksi kondisi`: Script mendeteksi internet mati + captive portal aktif
2. `Login otomatis`: Berhasil login dengan akun yang sudah dimasukan ke dalam script
3. `Gateway auth`: Token berhasil diotorisasi ke gateway lokal
4. `Internet terbuka`: Setelah login, internet langsung bekerja
5. `Smart check`: Saat dijalankan kedua kali, langsung detect internet sudah OK
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
┌→───→───→───→───→───→──→──→[SUKSES LOGIN]→──→──→──→──→──→─→[GAGAL]         
│                                  ▼                           ▼
│                                  │                           │
│                                  │                           │
│                [BYPASS Captive Portal For All Client]        │
│                                  │                           │
│           [LAN]┌─────────────────┘                           ▼
↑                ▼                                             │
│           [Tenda AC1200]                                     │         
│           Mode: AP                                           │
│           DHCP:192.168.1.0/24                                ▼
↑                │                                             │         
│          ┌─────┼─────┐                                       │         
│          │     │     │                                       │         
│        [User1][User2][User3]                                 │         
↑          │     │     │                                       ▼         
│      [Auth via Captive Portal]◄────◄────◄────◄─────◄────◄────│
│          │     │     │                                       ↑
↑          └────→┼◄────┘                                       ↑
│                │                                             ↑
│                ▼                                             ↑
└────────◄─[SUKSES LOGIN]───→[GAGAL]→────→────→────→────→──────┘
                 |
                 |
                 ▼ 
             [INTERNET]
```


## Install script:
```
mkdir /www/auto-Ruijie
cd /www/auto-Ruijie

# Simpan script
echo '[konten ruijie_auto_login_portal.py di atas]' > ruijie_auto_login_portal.py
echo '[konten monitor_ruijie.py di atas]' > monitor_ruijie.py <<<<<< OPSIONAL, menggunakan Crontab bisa saja

# Beri permission
chmod +x ruijie_auto_login_portal.py monitor_ruijie.py
dos2unix ruijie_auto_login_portal.py monitor_ruijie.py

# Install requests jika belum
pip3 install requests
```

<br>

## Konfigurasi Manual di dalam Script `ruijie_auto_login_portal.py`
ubah dan tambahkan account dan password untuk login.
`INTERFACE` = Lokasi interface target
`CREDENTIALS` = user dan passowrd login
`def setup_logging()` = lokasi penyimpanan file log
```
# ==================== KONFIGURASI ====================
INTERFACE = "eth1"
CREDENTIALS = [
    {"account": "Admin", "password": "Admin123"},  # Try admin first
    {"account": "Umum", "password": "Umum123"}  # Fallback to Umum
]

# ==================== SETUP LOGGING ====================
def setup_logging():
    log_dir = "/www/assisten/auto-Ruijie"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger('RuijieSmartLogin')
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler(f'{log_dir}/ruijie_smart.log')
    fh.setLevel(logging.INFO)
```

## Test script:
```
# Test smart login (hanya login jika diperlukan)
python3 ruijie_auto_login_portal.py

# Test monitor (check setiap 60 detik)
python3 monitor_ruijie.py
```

## SCRIPT MONITORING: `monitor_ruijie.py`

Opsional, tidak perlu jika sudah menggunakan CRONTAB saja.
<br>

```
#!/usr/bin/env python3
"""
Monitoring script untuk Ruijie connection
Jalankan sebagai service/daemon
"""

import time
import subprocess
import logging
import sys
import os
from datetime import datetime

# Setup logging
log_dir = "/www/auto-Ruijie"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_internet_quick():
    """Quick internet check"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def check_ruijie_portal():
    """Check if Ruijie portal is active"""
    try:
        import requests
        response = requests.get(
            "http://www.msftconnecttest.com/redirect",
            timeout=5,
            allow_redirects=False
        )
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            return 'portal-as.ruijienetworks.com' in location
        
        return False
    except:
        return False

def run_login_script():
    """Run the login script"""
    script_path = "/www/auto-Ruijie/ruijie_auto_login_portal.py"
    
    if os.path.exists(script_path):
        logger.info("Running login script...")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Login script successful")
            return True
        else:
            logger.error(f"Login script failed: {result.stderr}")
            return False
    else:
        logger.error(f"Login script not found: {script_path}")
        return False

def monitor_loop(check_interval=300):  # 5 minutes
    """Main monitoring loop"""
    logger.info("=" * 60)
    logger.info("Ruijie Connection Monitor Started")
    logger.info(f"Check interval: {check_interval} seconds")
    logger.info("=" * 60)
    
    last_status = None
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"\n[{current_time}] Checking connection...")
            
            # Check internet
            internet_ok = check_internet_quick()
            
            if internet_ok:
                logger.info("✅ Internet is working")
                
                if last_status != "online":
                    logger.info("Status changed: OFFLINE → ONLINE")
                    last_status = "online"
            else:
                logger.warning("❌ Internet not working")
                
                # Check if Ruijie portal is active
                portal_active = check_ruijie_portal()
                
                if portal_active:
                    logger.info("⚠ Ruijie captive portal detected, attempting login...")
                    
                    # Run login script
                    login_success = run_login_script()
                    
                    if login_success:
                        logger.info("✅ Login attempted")
                    else:
                        logger.error("❌ Login failed")
                else:
                    logger.info("⚠ No captive portal, might be network issue")
                
                if last_status != "offline":
                    logger.info("Status changed: ONLINE → OFFLINE")
                    last_status = "offline"
            
            # Wait for next check
            logger.info(f"Next check in {check_interval} seconds...")
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            logger.info("\n⚠ Monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    # Run as daemon or interactive
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        # Run as daemon
        import daemon
        from daemon import pidfile
        
        context = daemon.DaemonContext(
            working_directory='/www/auto-Ruijie',
            umask=0o002,
            pidfile=pidfile.PIDLockFile('/var/run/ruijie_monitor.pid'),
            stdout=open('/www/auto-Ruijie/monitor_out.log', 'w+'),
            stderr=open('/www/auto-Ruijie/monitor_err.log', 'w+')
        )
        
        with context:
            monitor_loop()
    else:
        # Run interactive
        monitor_loop(check_interval=60)  # 1 minute for testing
```


## Jalankan sebagai service: untuk menjalankan `monitor_ruijie.py`
```
# Buat init script
cat > /etc/init.d/ruijie_monitor << 'EOF'
#!/bin/sh /etc/rc.common
START=99
STOP=10

start() {
    /usr/bin/python3 /www/auto-Ruijie/monitor_ruijie.py daemon &
}

stop() {
    killall -9 python3
}
EOF

chmod +x /etc/init.d/ruijie_monitor

# Enable pada boot
/etc/init.d/ruijie_monitor enable
/etc/init.d/ruijie_monitor start
```

<br>

## Testing `ruijie_auto_login_portal.py` saat captive portal aktif dan otomatis berhasil login
```
root@Open-wrt:/# dos2unix /www/auto-Ruijie/ruijie_auto_login_portal.py
root@Open-wrt:/# chmod +x /www/auto-Ruijie/ruijie_auto_login_portal.py
root@Open-wrt:/# /www/auto-Ruijie/ruijie_auto_login_portal.py
2026-01-17 13:42:04 - INFO - ============================================================
2026-01-17 13:42:04 - INFO - SMART RUIJIE AUTO-LOGIN
2026-01-17 13:42:04 - INFO - Time: 2026-01-17 13:42:04
2026-01-17 13:42:04 - INFO - ============================================================
2026-01-17 13:42:04 - INFO - 
[1/5] Checking current internet status...
2026-01-17 13:42:04 - INFO - Testing internet connectivity...
2026-01-17 13:42:07 - INFO - ❌ Internet ping test: FAIL
2026-01-17 13:42:12 - INFO - ❌ HTTP test: FAIL
2026-01-17 13:42:12 - INFO - ⚠ Captive portal detected
2026-01-17 13:42:12 - INFO - 
[2/5] Checking for captive portal...
2026-01-17 13:42:12 - INFO - Checking for Ruijie captive portal...
2026-01-17 13:42:12 - INFO - Redirect location: https://portal-as.ruijienetworks.com/auth/wifidogAuth/login/?gw_id=984a6ba5d761&gw_sn=H1TB187004677&gw_address=192.168.110.1&gw_port=2060&ip=192.168.110.88&mac=05:f0:f5:08:be:31&slot_num=13&nasip=192.168.1.31&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2Fwww%2Emsftconnecttest%2Ecom%2Fredirect&chap_id=%5C107&chap_challenge=%5C146%5C307%5C060%5C353%5C146%5C226%5C344%5C374%5C011%5C212%5C011%5C362%5C171%5C177%5C066%5C334
2026-01-17 13:42:12 - INFO - ✅ Ruijie captive portal detected!
2026-01-17 13:42:12 - INFO - Captive portal parameters captured
2026-01-17 13:42:12 - INFO - Gateway: 192.168.110.1
2026-01-17 13:42:12 - INFO - MAC: 05:f0:f5:08:be:31
2026-01-17 13:42:12 - INFO - 
[3/5] Getting session ID...
2026-01-17 13:42:12 - INFO - Accessing login page...
2026-01-17 13:42:13 - INFO - Getting session ID...
2026-01-17 13:42:13 - INFO - ✅ Session ID: b2f1d91faa1e4525a8d1bed6e7e3d3e4
2026-01-17 13:42:13 - INFO - 
[4/5] Attempting login...
2026-01-17 13:42:13 - INFO - Trying credentials: Umum
2026-01-17 13:42:13 - INFO - Trying login with: Umum
2026-01-17 13:42:13 - INFO - ✅ Login response: {
  "success": true,
  "timestamp": 1768632133215,
  "result": {
    "authResult": "1",
    "logonUrl": "http://192.168.110.1:2060/wifidog/auth?token=b2f1d91faa1e4525a8d1bed6e7e3d3e4&phoneNumber=Umum",
    "modifyPwd": null
  },
  "message": null
}
2026-01-17 13:42:13 - INFO - 🎉 Login successful as: Umum
2026-01-17 13:42:13 - INFO - 
[5/5] Authorizing gateway...
2026-01-17 13:42:13 - INFO - Authorizing gateway: http://192.168.110.1:2060/wifidog/auth
2026-01-17 13:42:13 - INFO - Gateway auth status: 302
2026-01-17 13:42:13 - INFO - Redirected to: https://portal-as.ruijienetworks.com/auth/wifidogAuth/portal/?gw_id=984a6ba5d761&gw_sn=H1TB187004677&ip=192.168.110.88&mac=05:f0:f5:08:be:31
2026-01-17 13:42:13 - INFO - ✅ Gateway authorized
2026-01-17 13:42:13 - INFO - 
[6/5] Verifying internet access...
2026-01-17 13:42:16 - INFO - Waiting for internet (max 15s)...
2026-01-17 13:42:16 - INFO - Testing internet connectivity...
2026-01-17 13:42:17 - INFO - ✅ Internet ping test: PASS
2026-01-17 13:42:17 - INFO - ✅ Internet is now working!
2026-01-17 13:42:17 - INFO - ============================================================
2026-01-17 13:42:17 - INFO - 🎉 SUCCESS! Internet access granted
2026-01-17 13:42:17 - INFO - ============================================================
2026-01-17 13:42:17 - INFO - 
✅ Script completed successfully
root@Open-wrt:/# 
```

<br>

## Testing `ruijie_auto_login_portal.py` saat berhasil login sebelumnya dan terbaca sudah Login
```
root@Open-wrt:/# /www/auto-Ruijie/ruijie_auto_login_portal.py
2026-01-17 13:43:04 - INFO - ============================================================
2026-01-17 13:43:04 - INFO - SMART RUIJIE AUTO-LOGIN
2026-01-17 13:43:04 - INFO - Time: 2026-01-17 13:43:04
2026-01-17 13:43:04 - INFO - ============================================================
2026-01-17 13:43:04 - INFO - 
[1/5] Checking current internet status...
2026-01-17 13:43:04 - INFO - Testing internet connectivity...
2026-01-17 13:43:05 - INFO - ✅ Internet ping test: PASS
2026-01-17 13:43:07 - INFO - ✅ HTTP test: PASS
2026-01-17 13:43:07 - INFO - ✅ No captive portal (Microsoft redirect)
2026-01-17 13:43:07 - INFO - Internet tests: 3/3 passed
2026-01-17 13:43:07 - INFO - 🎉 Internet already working, no action needed!
2026-01-17 13:43:07 - INFO - 
✅ Script completed successfully
root@Open-wrt:/# 
```

<br>

## 📊 Data Penting dari Log:
```
Session ID: b2f1d91faa1e4525a8d1bed6e7e3d3e4
Akun yang berhasil: Umum
MAC yang digunakan: 05:f0:f5:08:be:31 (MAC Tenda O3V2)
Gateway: 192.168.110.1:2060
```
```
2026-01-17 13:42:13 - INFO - ✅ Login response: {
  "success": true,
  "timestamp": 1768632133215,
  "result": {
    "authResult": "1",
    "logonUrl": "http://192.168.110.1:2060/wifidog/auth?token=b2f1d91faa1e4525a8d1bed6e7e3d3e4&phoneNumber=Umum",
    "modifyPwd": null
  },
  "message": null
}
```
