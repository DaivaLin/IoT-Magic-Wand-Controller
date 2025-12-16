import machine
import time

# --- 設定區 ---
# 紀錄時間 (秒)
RECORD_SECONDS = 30 
# 取樣頻率 (每秒幾次)
SAMPLE_RATE = 10 
# 檔案名稱
LOG_FILE = "motion_log.txt"

# --- 硬體設定 ---
adc_x = machine.ADC(2) # GP28
adc_y = machine.ADC(1) # GP27
led = machine.Pin('LED', machine.Pin.OUT)

def blink_ready():
    """準備階段：快閃 5 秒"""
    print("準備中... (請就定位)")
    for _ in range(25): # 0.2s * 25 = 5秒
        led.toggle()
        time.sleep(0.2)
    led.off()

def start_logging():
    """開始寫入檔案"""
    print(f"開始紀錄！數據將寫入 {LOG_FILE}")
    
    # 使用 'w' 模式 (每次都會覆蓋舊檔案，確保是最新的數據)
    with open(LOG_FILE, "w") as f:
        # 寫入標題
        f.write("Time_ms, X_Value, Y_Value\n")
        
        start_time = time.ticks_ms()
        total_samples = RECORD_SECONDS * SAMPLE_RATE
        delay_time = 1.0 / SAMPLE_RATE
        
        for i in range(total_samples):
            # 1. 讀取數據
            x = adc_x.read_u16()
            y = adc_y.read_u16()
            current_time = time.ticks_diff(time.ticks_ms(), start_time)
            
            # 2. 格式化寫入 (例如: 1500, 16500, 14200)
            line = f"{current_time}, {x}, {y}\n"
            f.write(line)
            
            # 3. 狀態指示 (慢閃：錄製中)
            if i % 5 == 0: # 每 5 次迴圈閃一下
                led.toggle()
            
            # 4. 控制採樣速度
            time.sleep(delay_time)
            
    print("紀錄完成！")
    # 結束指示：恆亮
    led.on()

# --- 主程式 ---
try:
    blink_ready()    # 倒數
    start_logging()  # 錄製
except Exception as e:
    # 如果出錯 (例如硬碟滿了)，快速狂閃警示
    print(f"錯誤: {e}")
    while True:
        led.toggle()
        time.sleep(0.05)