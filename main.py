import os
import hashlib
import time
import json
import requests
from datetime import datetime

# --- သင်ရလာတဲ့ Publish to web CSV Link ကို ဒီမှာ ထည့်ပါ ---
SHEET_CSV_URL = "ဒီနေရာမှာ_CSV_Link_ကိုအစားထိုးပါ"
LICENSE_FILE = ".session_data"

def get_unique_id():
    """ဖုန်းတစ်လုံးချင်းစီအတွက် မပြောင်းလဲသော Unique ID ထုတ်ပေးခြင်း"""
    try:
        # Termux အတွက် Android ID ကို ယူခြင်း
        android_id = os.popen("settings get secure android_id").read().strip()
        if not android_id or "null" in android_id:
            # တကယ်လို့ မရရင် Hardware info တွေကို သုံးမယ်
            import platform
            android_id = f"{platform.node()}-{platform.processor()}"
        
        unique_hash = hashlib.md5(android_id.encode()).hexdigest().upper()
        return f"KN-{unique_hash[:12]}"
    except:
        return "KN-UNKNOWN-DEVICE"

def check_online(my_id):
    """Google Sheet မှ ID နှင့် ရက်စွဲကို စစ်ဆေးခြင်း"""
    try:
        response = requests.get(SHEET_CSV_URL, timeout=10)
        if response.status_code != 200:
            return False, "Server Error"
            
        lines = response.text.splitlines()
        for line in lines:
            parts = line.split(',')
            if len(parts) >= 2:
                s_id = parts[0].strip()
                s_expiry = parts[1].strip()
                s_status = parts[2].strip() if len(parts) > 2 else "Active"
                
                if s_id == my_id and s_status.lower() == "active":
                    # Offline သုံးနိုင်ရန် သိမ်းဆည်းခြင်း
                    with open(LICENSE_FILE, "w") as f:
                        json.dump({"id": my_id, "expiry": s_expiry}, f)
                    return True, s_expiry
        return False, "Unauthorized"
    except:
        return False, "Connection Error"

def check_offline(my_id):
    """Offline စစ်ဆေးခြင်း"""
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
    
    # ၁။ Offline အရင်စစ်မယ်
    valid, expiry = check_offline(my_id)
    
    # ၂။ Offline မရရင် (သို့မဟုတ်) ပထမဆုံးအကြိမ်ဆိုရင် Online စစ်မယ်
    if not valid:
        print("[*] Validating license online...")
        valid, expiry = check_online(my_id)
        
    if valid:
        print(f"[+] Access Granted! Expiry: {expiry}")
        print("-" * 35)
        # --- ဤနေရာတွင် သင့်၏ starlink.so ကို ခေါ်သုံးပါ ---
        try:
            import starlink
            starlink.main() # သို့မဟုတ် starlink.start()
        except ImportError:
            print("[!] starlink.so file ကို ရှာမတွေ့ပါ။")
    else:
        print(f"[!] Access Denied. Your ID is not registered or expired.")
        print(f"Please send your ID to Admin: {my_id}")

if __name__ == "__main__":
    main()
