import os, hashlib, requests

# ၁။ စက်ရဲ့ ID (HWID) ကို ထုတ်ယူပုံ
def get_hwid():
    model = os.popen("getprop ro.product.model").read().strip()
    serial = os.popen("getprop ro.serialno").read().strip()
    hwid_raw = f"{model}{serial}"
    return hashlib.md5(hwid_raw.encode()).hexdigest().upper()

# ၂။ အွန်လိုင်းကနေ လိုင်စင်စစ်ဆေးပုံ
KEY_URL = "https://raw.githubusercontent.com/ytun9959-design/Auth/refs/heads/main/key.txt"

def perform_online_check():
    my_id = get_hwid()
    response = requests.get(KEY_URL).text
    # key.txt ထဲမှာ ID|KEY|EXPIRY ပုံစံနဲ့ ရှိနေတာကို စစ်ဆေးတာပါ
    for line in response.split('\n'):
        if my_id in line:
            server_key = line.split('|')[1]
            user_key = input("Activation Key ထည့်ပါ: ")
            if user_key == server_key:
                print("လိုင်စင် အောင်မြင်ပါတယ်!")
                return True
    print("လိုင်စင် မရှိပါ သို့မဟုတ် Key မှားနေပါတယ်။")
    return False
    
