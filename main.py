import os
import hashlib
import json
import requests
import csv
import time
from datetime import datetime

# --- GitHub Raw Link ---
GITHUB_RAW_URL = "https://raw.githubusercontent.com/demoppal/gg/refs/heads/main/gg.txt"
LICENSE_FILE = ".session_data"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- ANSI UI Colors ---
C_BLUE    = "\033[94m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_RED     = "\033[91m"
C_CYAN    = "\033[96m"
C_WHITE   = "\033[97m"  # <--- ဒီကောင်လေး ကျန်ခဲ့လို့ အခု ထည့်ပေးလိုက်ပါပြီ
C_BOLD    = "\033[1m"
C_END     = "\033[0m"

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def show_banner(my_id):
    clear_screen()
    print(f"{C_CYAN}{C_BOLD}" + "="*45)
    print(f"        PREMIUM KEY VALIDATION SYSTEM        ")
    print(f"="*45 + f"{C_END}")
    print(f"{C_BOLD} YOUR DEVICE ID : {C_YELLOW}{my_id}{C_END}")
    print(f"{C_CYAN}" + "-"*45 + f"{C_END}")

def get_unique_id():
    try:
        android_id = os.popen("settings get secure android_id").read().strip()
        if not android_id or "null" in android_id:
            import platform
            android_id = f"{platform.node()}-{platform.processor()}"
        
        unique_hash = hashlib.md5(android_id.encode()).hexdigest().upper()
        return f"KN-{unique_hash[:10]}"
    except Exception:
        return "KN-UNKNOWN"

def is_expired(expiry_str):
    try:
        expiry_dt = datetime.strptime(expiry_str, DATE_FORMAT)
        return datetime.now() > expiry_dt
    except ValueError:
        return True

def check_online(my_id):
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=10)
        if response.status_code != 200:
            return False, "Server Error (GitHub Offline)"
            
        lines = response.text.splitlines()
        reader = csv.reader(lines)
        
        for row in reader:
            if len(row) >= 2:
                s_id = row[0].strip()
                s_expiry = row[1].strip()
                
                if s_id == my_id:
                    if is_expired(s_expiry):
                        return False, "License Expired"
                        
                    # အောင်မြင်ရင် နောက်တစ်ခါ Offline သုံးလို့ရအောင် ဖုန်းထဲမှာ သိမ်းဆည်းမယ်
                    with open(LICENSE_FILE, "w") as f:
                        json.dump({"id": my_id, "expiry": s_expiry}, f)
                    return True, s_expiry
                    
        return False, "Unauthorized"
    except requests.RequestException:
        return False, "Connection Error"
    except Exception:
        return False, "System Error"

def check_offline(my_id):
    if not os.path.exists(LICENSE_FILE):
        return False, None
    try:
        with open(LICENSE_FILE, "r") as f:
            data = json.load(f)
            
        if data.get('id') == my_id:
            expiry_str = data.get('expiry')
            if not is_expired(expiry_str):
                return True, expiry_str
    except Exception:
        pass
    return False, None

def run_starlink():
    print(f"\n{C_GREEN}[*] Launching Starlink Module...{C_END}")
    time.sleep(1)
    try:
        import starlink
        if hasattr(starlink, 'main'):
            starlink.main()
        elif hasattr(starlink, 'start'):
            starlink.start()
        else:
            print(f"{C_RED}[!] Error: Starlink main/start function not found.{C_END}")
    except ImportError:
        print(f"{C_RED}[!] Error: 'starlink.so' or 'starlink.py' file missing.{C_END}")

def main():
    my_id = get_unique_id()
    
    while True:
        show_banner(my_id)
        
        # ၁။ Offline အရင်စစ်မယ်
        valid, expiry = check_offline(my_id)
        
        # ၂။ Offline အဆင်မပြေရင် (သို့) သက်တမ်းကုန်နေရင် Online ထပ်စစ်မယ်
        if not valid:
            print(f"{C_BLUE}[*] Checking license online via GitHub...{C_END}")
            time.sleep(1)
            valid, expiry = check_online(my_id)
            
        if valid:
            print(f"\n{C_GREEN}{C_BOLD}[+] ACCESS GRANTED!{C_END}")
            print(f"{C_BOLD} Expiry Date   : {C_YELLOW}{expiry}{C_END}")
            print(f"{C_CYAN}" + "="*45 + f"{C_END}")
            run_starlink()
            break
        else:
            print(f"\n{C_RED}{C_BOLD}[!] ACCESS DENIED: {expiry}{C_END}")
            print(f"{C_WHITE} ID ကို GitHub ထဲမှာ အရင်သွားထည့်ပေးပါ။{C_END}")
            print(f"{C_CYAN}" + "-"*45 + f"{C_END}")
            
            # Enter ခေါက်ပြီး ပြန်စစ်ခိုင်းမယ့်နေရာ
            input(f"{C_BOLD}{C_BLUE}[►] ID ထည့်ပြီးပါက Re-check လုပ်ရန် ENTER ခေါက်ပါ... {C_END}")

if __name__ == "__main__":
    main()
