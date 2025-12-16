import machine
import time

# --- 設定區 ---
# 你的麥克風 D0 接在 GP17
PIN_MIC = 17 

# 為了方便觀察，我們用 Pico 板子上的 LED 來同步顯示
# 有聲音 -> 亮燈
# 沒聲音 -> 滅燈
led = machine.Pin('LED', machine.Pin.OUT)
mic = machine.Pin(PIN_MIC, machine.Pin.IN)

print("🎤 麥克風測試開始！")
print("請轉動藍色旋鈕調整靈敏度...")
print("目標：安靜時顯示 0 (滅燈)，有聲音時顯示 1 (亮燈)")
print("-" * 30)

while True:
    # 讀取麥克風數位訊號 (0 或 1)
    val = mic.value()
    
    if val == 1:
        # 偵測到聲音！
        print(f"🔊 聲音! ({val})")
        led.on()  # 亮燈
        
        # 稍微延遲一下，讓你眼睛看得到閃爍
        time.sleep(0.1) 
        led.off() # 滅燈
    else:
        # 安靜無聲
        # 為了不要讓 Shell 視窗洗版，我們安靜時不印東西，或者只印一個點
        # print(".", end="") 
        led.off()
        
    # 極短的延遲，讓處理器全速掃描
    time.sleep(0.01)