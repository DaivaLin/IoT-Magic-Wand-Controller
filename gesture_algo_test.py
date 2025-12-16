import machine
import time

# --- [數據分析區] 根據先前測試提供的數值 ---
# 朝上: X~16800, Y~13600
# 朝下: X~14000, Y~13300
# 朝左: X~13500, Y~16400 (Y很高)
# 朝右: X~14700, Y~10800 (Y很低)

# --- [判定邏輯] ---
# 為了鎖定 "上下"，我們必須限制 Y 只能在中間範圍 (12000~15000)
# 這樣可以防止 "左" (Y>16000) 和 "右" (Y<11000) 被誤判成 "下"

def get_pose(x, y):
    """回傳目前的姿勢: UP, DOWN, 或 OTHER"""
    
    # 先檢查 Y 軸是否在「中間區域」 (排除左右)
    # 你的上下動作 Y 都在 13000 多，所以我們設寬一點 12000~15000
    if 12000 < y < 15000:
        
        # 在 Y 軸正確的前提下，才看 X 軸
        if x > 16000:
            return "UP"   # 朝上
        elif x < 16000:
            return "DOWN" # 朝下
            
    return "OTHER" # 其他姿勢 (可能是左、右、或平放)

# --- 硬體設定 ---
adc_x = machine.ADC(2) # GP28
adc_y = machine.ADC(1) # GP27
led = machine.Pin('LED', machine.Pin.OUT)

# 狀態變數
is_armed = False       # 是否已上膛 (朝上過)
action_started = False # 是否已開始動作 (下壓過)
last_time = 0
TIMEOUT = 1000         # 動作要在 1 秒內完成

def fire_skill():
    print("\n>>> ⚔️⚔️ [技能發動] 完美判定：上 -> 下 -> 上 ⚔️⚔️")
    # ble.write(b'SKILL')
    for _ in range(5):
        led.toggle()
        time.sleep(0.05)

print("系統啟動！請將板子 [朝上] 準備...")

while True:
    # 1. 讀取數據
    x = adc_x.read_u16()
    y = adc_y.read_u16()
    
    # 2. 判斷姿勢 (同時看 X 和 Y)
    pose = get_pose(x, y)
    now = time.ticks_ms()
    
    # --- 狀態機邏輯 ---
    
    # [狀態 A] 朝上 (UP)
    if pose == "UP":
        # 如果之前已經完成 "朝下" (action_started)，現在又回到 "朝上" -> 發射！
        if action_started:
            fire_skill()
            action_started = False # 重置
            
        # 只要回到朝上，就標記為 "已上膛" (Armed)
        if not is_armed:
            is_armed = True
            print(f"狀態: 已上膛 (Ready) - X:{x}, Y:{y}")
            led.on() # 亮燈表示準備好

    # [狀態 B] 朝下 (DOWN)
    elif pose == "DOWN":
        # 只有在 "已上膛" 的情況下，朝下才有效
        if is_armed:
            if not action_started:
                print(f"動作開始: 向下偵測! (X:{x}, Y:{y})")
                action_started = True
                last_time = now
                led.off() # 燈滅表示動作中
        else:
            # 如果一開始就朝下 (沒有先朝上)，什麼都不做 (嚴格禁止下往上)
            pass

    # [狀態 C] 其他 (Left / Right / Unknown)
    else:
        # 如果亂晃到左邊或右邊，為了安全，取消目前的蓄力
        if action_started:
             print("動作取消 (姿勢偏移)")
             action_started = False
             is_armed = False
             led.off()

    # 超時檢查 (如果往下之後，太久沒回來)
    if action_started and (now - last_time > TIMEOUT):
        print("--- 超時，動作失效 ---")
        action_started = False
        is_armed = False # 需重新上膛
        led.off()

    time.sleep(0.05)