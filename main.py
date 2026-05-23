import os
import hashlib
import time
import json
import requests
from datetime import datetime

# --- သင့်ရဲ့ Google Sheet CSV Link ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/14yK0foxzyjI7ZyYRPtEWAkO4ifG1EgITAttE8T_8YBE/export?format=csv"
LICENSE_FILE = ".session_data"

def get_unique_id():
    try:
        # Android ID ကို ယူခြင်း
        android_id = os.popen("settings get secure android_id").read().strip()
        if not android_id or "null" in android_id:
            import platform
            android_id = f"{platform.node()}-{platform.processor()}"
        
        unique_hash = hashlib.md5(android_id.encode()).hexdigest().upper()
        # သင့်ပုံထဲကအတိုင်း KN- နောက်မှာ ၁၀ လုံးပဲ ယူပါမယ်
        return f"KN-{unique_hash[:10]}"
    except:
        return "KN-UNKNOWN"

def check_online(my_id):
    try:
        # Google Sheet မှ CSV ကို ဖတ်ခြင်း
        response = requests.get(SHEET_CSV_URL, timeout=10)
        lines = response.text.splitlines()
        
        for line in lines:
            parts = line.split(',')
            if len(parts) >= 2:
                s_id = parts[0].strip()
                s_expiry = parts[1].strip()
                
                if s_id == my_id:
                    # အောင်မြင်ရင် Offline အတွက် သိမ်းမယ်
                    with open(LICENSE_FILE, "w") as f:
                        json.dump({"id": my_id, "expiry": s_expiry}, f)
                    return True, s_expiry
        return False, "Unauthorized"
    except Exception as e:
        return False, f"Connection Error"

def check_offline(my_id):
    if not os.path.exists(LICENSE_FILE):
        return False, None
    try:
        with open(LICENSE_FILE, "r") as f:
            data = json.load(f)
        if data['id'] == my_id:
            expiry_dt = datetime.strptime(data['expiry'], "%Y-%m-%d %H:%M:%S")
            if datetime.now() < expiry_dt:
                return True, data['expiry']
    except:
        pass
    return False, None

def main():
    my_id = get_unique_id()
    os.system("clear")
    print(f"--- DEVICE ID: {my_id} ---")
    
    # ၁။ Offline အရင်စစ်
    valid, expiry = check_offline(my_id)
    
    # ၂။ မရရင် Online စစ်
    if not valid:
        print("[*] Checking license online...")
        valid, expiry = check_online(my_id)
        
    if valid:
        print(f"[+] Access Granted! Expiry: {expiry}")
        print("-" * 35)
        # --- starlink.so ကို ခေါ်ယူခြင်း ---
        try:
            import starlink
            # starlink ထဲက main သို့မဟုတ် start ကို ခေါ်ပါ
            if hasattr(starlink, 'main'):
                starlink.main()
            elif hasattr(starlink, 'start'):
                starlink.start()
        except ImportError:
            print("[!] starlink.so file မရှိပါ။")
    else:
        print(f"[!] Access Denied. Your ID is not registered.")
        print(f"Please add this ID to Google Sheet: {my_id}")

if __name__ == "__main__":
    main()
