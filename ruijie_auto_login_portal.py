#!/usr/bin/env python3
"""
Smart Ruijie Auto-Login Script
- Hanya login jika benar-benar diperlukan
- Tidak perlu mengubah MAC jika tidak perlu
- Gunakan credentials umum
"""

import requests
import json
import time
import logging
import sys
import re
import subprocess
import os
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime

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
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = setup_logging()

class RuijieSmartLogin:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        requests.packages.urllib3.disable_warnings()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        self.eth2_ip = None
        self.session_id = None
        self.auth_params = {}
        
    # ==================== UTILITY FUNCTIONS ====================
    def run_cmd(self, cmd):
        """Run shell command"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def get_interface_info(self):
        """Get interface IP and MAC"""
        # Get IP
        code, out, err = self.run_cmd(f"ip -4 addr show {INTERFACE}")
        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', out)
        ip = match.group(1) if match else None
        
        # Get MAC
        code, out, err = self.run_cmd(f"cat /sys/class/net/{INTERFACE}/address")
        mac = out.strip() if out else None
        
        return ip, mac
    
    def check_internet_access(self, quick=False):
        """Check if internet is already working"""
        tests = []
        
        # Test 1: Ping
        logger.info("Testing internet connectivity...")
        code, out, err = self.run_cmd("ping -c 2 -W 2 8.8.8.8")
        if code == 0:
            logger.info("✅ Internet ping test: PASS")
            tests.append(True)
        else:
            logger.info("❌ Internet ping test: FAIL")
            tests.append(False)
        
        if quick:
            return any(tests)
        
        # Test 2: HTTP
        try:
            response = requests.get(
                "http://www.google.com",
                timeout=5,
                allow_redirects=False,
                verify=False
            )
            if response.status_code in [200, 302]:
                logger.info("✅ HTTP test: PASS")
                tests.append(True)
            else:
                logger.info(f"❌ HTTP test: FAIL ({response.status_code})")
                tests.append(False)
        except:
            logger.info("❌ HTTP test: FAIL")
            tests.append(False)
        
        # Test 3: Captive portal test
        try:
            response = requests.get(
                "http://www.msftconnecttest.com/redirect",
                timeout=5,
                allow_redirects=False,
                verify=False
            )
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if 'portal-as.ruijienetworks.com' in location:
                    logger.info("⚠ Captive portal detected")
                    return False  # Internet blocked by captive portal
                else:
                    logger.info("✅ No captive portal (Microsoft redirect)")
                    tests.append(True)
            elif response.status_code == 200:
                logger.info("✅ No captive portal (direct access)")
                tests.append(True)
            else:
                logger.info(f"⚠ Unexpected status: {response.status_code}")
                tests.append(False)
        except:
            logger.info("❌ Portal test: FAIL")
            tests.append(False)
        
        # If at least 2 tests pass, consider internet working
        success_count = sum(tests)
        logger.info(f"Internet tests: {success_count}/{len(tests)} passed")
        
        return success_count >= 2
    
    def check_ruijie_captive_portal(self):
        """Specifically check for Ruijie captive portal"""
        try:
            logger.info("Checking for Ruijie captive portal...")
            
            response = self.session.get(
                "http://www.msftconnecttest.com/redirect",
                timeout=5,
                allow_redirects=False
            )
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                logger.info(f"Redirect location: {location}")
                
                if 'portal-as.ruijienetworks.com' in location:
                    logger.info("✅ Ruijie captive portal detected!")
                    
                    # Parse parameters
                    parsed = urlparse(location)
                    params = parse_qs(parsed.query)
                    
                    # Get current IP and MAC
                    current_ip, current_mac = self.get_interface_info()
                    
                    self.auth_params = {
                        'gw_id': params.get('gw_id', [''])[0],
                        'gw_sn': params.get('gw_sn', [''])[0],
                        'gw_address': params.get('gw_address', [''])[0],
                        'gw_port': params.get('gw_port', [''])[0],
                        'ip': current_ip,
                        'mac': params.get('mac', [current_mac])[0],  # Use MAC from redirect or current
                        'slot_num': params.get('slot_num', [''])[0],
                        'nasip': params.get('nasip', [''])[0],
                        'ssid': params.get('ssid', [''])[0],
                        'url': 'http://www.msftconnecttest.com/redirect',
                        'ustate': params.get('ustate', ['0'])[0],
                        'mac_req': params.get('mac_req', ['1'])[0]
                    }
                    
                    # Add CHAP parameters if present
                    for key in ['chap_id', 'chap_challenge']:
                        if params.get(key):
                            self.auth_params[key] = params.get(key, [''])[0]
                    
                    logger.info(f"Captive portal parameters captured")
                    logger.info(f"Gateway: {self.auth_params.get('gw_address')}")
                    logger.info(f"MAC: {self.auth_params.get('mac')}")
                    
                    return True
                else:
                    logger.info(f"No Ruijie portal (redirects to: {location[:50]}...)")
                    return False
            else:
                logger.info(f"No redirect (status: {response.status_code})")
                return False
                
        except Exception as e:
            logger.error(f"Error checking portal: {e}")
            return False
    
    def get_session_id(self):
        """Get session ID from Ruijie portal"""
        try:
            # Step 1: Access login page
            login_url = "https://portal-as.ruijienetworks.com/auth/wifidogAuth/login/"
            logger.info(f"Accessing login page...")
            
            response = self.session.get(
                login_url,
                params=self.auth_params,
                timeout=10
            )
            
            # Step 2: Get session via API
            api_url = "https://portal-as.ruijienetworks.com/api/auth/wifidog"
            api_params = self.auth_params.copy()
            api_params['stage'] = 'portal'
            
            logger.info("Getting session ID...")
            response = self.session.get(
                api_url,
                params=api_params,
                timeout=10,
                allow_redirects=True
            )
            
            # Extract session ID from redirect chain
            session_id = None
            for resp in [response] + response.history:
                # Check URL
                if 'sessionId=' in resp.url:
                    match = re.search(r'sessionId=([a-f0-9]+)', resp.url)
                    if match:
                        session_id = match.group(1)
                        break
                
                # Check Location header
                location = resp.headers.get('Location', '')
                if 'sessionId=' in location:
                    match = re.search(r'sessionId=([a-f0-9]+)', location)
                    if match:
                        session_id = match.group(1)
                        break
            
            if session_id:
                self.session_id = session_id
                logger.info(f"✅ Session ID: {session_id}")
                return True
            else:
                logger.error("❌ No session ID found")
                logger.debug(f"Final URL: {response.url}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return False
    
    def try_login_with_credentials(self, credentials):
        """Try login with given credentials"""
        try:
            payload = {
                "account": credentials["account"],
                "password": credentials["password"],
                "sessionId": self.session_id,
                "apiVersion": 1
            }
            
            headers = {'Content-Type': 'application/json'}
            
            logger.info(f"Trying login with: {credentials['account']}")
            
            response = self.session.post(
                "https://portal-as.ruijienetworks.com/api/auth/fixedAccount/maccInter?lang=en_ID",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"✅ Login response: {json.dumps(data, indent=2)}")
                    
                    # Check if login successful
                    if data.get('success') and data.get('result', {}).get('authResult') == '1':
                        logger.info(f"🎉 Login successful as: {credentials['account']}")
                        return True
                    else:
                        logger.warning(f"Login not successful: {data}")
                        return False
                except json.JSONDecodeError:
                    logger.info("✅ Login successful (non-JSON response)")
                    return True
            else:
                logger.error(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def authorize_gateway(self):
        """Authorize with local gateway"""
        try:
            if not self.auth_params.get('gw_address'):
                logger.warning("No gateway address, skipping auth")
                return True
            
            gateway_url = f"http://{self.auth_params['gw_address']}:2060/wifidog/auth"
            
            # Use the first credential for gateway auth
            params = {
                'token': self.session_id,
                'phoneNumber': CREDENTIALS[0]["account"]  # Use "Umum"
            }
            
            logger.info(f"Authorizing gateway: {gateway_url}")
            
            response = self.session.get(
                gateway_url,
                params=params,
                timeout=10,
                allow_redirects=False
            )
            
            logger.info(f"Gateway auth status: {response.status_code}")
            
            if response.status_code in [200, 302]:
                location = response.headers.get('Location', '')
                if location:
                    logger.info(f"Redirected to: {location}")
                
                logger.info("✅ Gateway authorized")
                return True
            else:
                logger.warning(f"Gateway auth failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Gateway auth error: {e}")
            return False
    
    def wait_for_internet(self, timeout=30):
        """Wait for internet to become available"""
        logger.info(f"Waiting for internet (max {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_internet_access(quick=True):
                logger.info("✅ Internet is now working!")
                return True
            
            logger.info("Waiting...")
            time.sleep(5)
        
        logger.warning("⚠ Internet not available after waiting")
        return False
    
    def cleanup(self):
        """Cleanup session"""
        self.session.close()
    
    # ==================== MAIN LOGIC ====================
    def run(self):
        """Main execution logic"""
        logger.info("=" * 60)
        logger.info("SMART RUIJIE AUTO-LOGIN")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Step 1: Check current internet status
        logger.info("\n[1/5] Checking current internet status...")
        if self.check_internet_access():
            logger.info("🎉 Internet already working, no action needed!")
            return True
        
        # Step 2: Check for Ruijie captive portal
        logger.info("\n[2/5] Checking for captive portal...")
        if not self.check_ruijie_captive_portal():
            logger.error("❌ No Ruijie captive portal detected")
            logger.info("Possible reasons:")
            logger.info("1. Internet already working (check failed earlier)")
            logger.info("2. Different captive portal system")
            logger.info("3. Network connectivity issue")
            return False
        
        # Step 3: Get session ID
        logger.info("\n[3/5] Getting session ID...")
        if not self.get_session_id():
            logger.error("❌ Failed to get session ID")
            return False
        
        # Step 4: Try login with different credentials
        logger.info("\n[4/5] Attempting login...")
        login_success = False
        
        for creds in CREDENTIALS:
            logger.info(f"Trying credentials: {creds['account']}")
            if self.try_login_with_credentials(creds):
                login_success = True
                break
            else:
                logger.info(f"Failed with {creds['account']}, trying next...")
        
        if not login_success:
            logger.error("❌ All login attempts failed")
            return False
        
        # Step 5: Authorize gateway
        logger.info("\n[5/5] Authorizing gateway...")
        self.authorize_gateway()
        
        # Step 6: Wait and verify
        logger.info("\n[6/5] Verifying internet access...")
        time.sleep(3)  # Short wait
        
        if self.wait_for_internet(timeout=15):
            logger.info("=" * 60)
            logger.info("🎉 SUCCESS! Internet access granted")
            logger.info("=" * 60)
            return True
        else:
            logger.warning("⚠ Login may have succeeded but internet not verified")
            
            # Final check
            if self.check_internet_access(quick=True):
                logger.info("✅ Internet is actually working!")
                return True
            else:
                logger.error("❌ Internet still not working after login")
                return False

def main():
    """Main function"""
    login = RuijieSmartLogin()
    
    try:
        success = login.run()
        login.cleanup()
        
        if success:
            logger.info("\n✅ Script completed successfully")
        else:
            logger.error("\n❌ Script failed")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("\n⚠ Interrupted by user")
        login.cleanup()
        return 0
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        login.cleanup()
        return 1

if __name__ == "__main__":
    sys.exit(main())
