import starlink
import os

def start_tool():
    # လိုင်စင်စစ်ဆေးမှု အောင်မြင်ရင် starlink binary ထဲက logic တွေကို ခေါ်သုံးတယ်
    if perform_online_check():
        print("Status: Active")
        # starlink.so ထဲက main သို့မဟုတ် start function ကို ခေါ်တယ်
        starlink.start() 
    else:
        exit()
