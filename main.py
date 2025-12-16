import uasyncio as asyncio
import aioble
import bluetooth
import machine
import ubinascii
import time

# ==========================================
# [1. 設定區]
# ==========================================

# 藍牙
TARGET_ADDR_STR = "E4:66:E5:8E:2E:97"
TARGET_ADDR_BYTES = ubinascii.unhexlify(TARGET_ADDR_STR.replace(":", ""))
SERVICE_UUID = bluetooth.UUID(0xFFF0) 
CHAR_UUID = bluetooth.UUID(0xFFF2)

CMD_OPEN  = bytes([0x43, 0x02, 0x01, 0x01])
CMD_CLOSE = bytes([0x43, 0x02, 0x01, 0x02])

STATE_FILE = "state.txt"

# --- [關鍵修改] 體感參數 (只看 X 軸) ---
# 你的平放基準大約是 16800
# 你要求的變化量是 1800
# 16800 - 1800 = 15000
X_UP_RESET   = 14500  # 回到這個數值以上，視為「歸位/上膛」
X_DOWN_TRIG  = 13800  # 掉到這個數值以下，視為「點頭/觸發」
GESTURE_TIMEOUT = 1000 

# 硬體 (Y 軸已移除)
adc_x = machine.ADC(2)
pin_mic = machine.Pin(17, machine.Pin.IN)
led = machine.Pin('LED', machine.Pin.OUT)

# 全域變數
ble_connection = None
ble_characteristic = None
last_gesture_time = 0  
last_voice_time = 0    
COMBO_WINDOW = 2500    

# ==========================================
# [2. 核心邏輯]
# ==========================================

def read_last_state():
    try:
        with open(STATE_FILE, "r") as f:
            return True if f.read().strip() == "1" else False
    except OSError:
        return False

def save_current_state(is_on):
    try:
        with open(STATE_FILE, "w") as f:
            f.write("1" if is_on else "0")
    except OSError:
        pass

current_switch_state = read_last_state()
print(f"🔄 系統回復：上次狀態為 [{'開' if current_switch_state else '關'}]")

def get_x_pose(x):
    """只看 X 軸的姿勢判定"""
    if x > X_UP_RESET:
        return "UP"   # 數值高 (板子立起來/朝上)
    elif x < X_DOWN_TRIG:
        return "DOWN" # 數值低 (板子倒下去/點頭)
    return "MID"      # 中間過渡狀態

async def check_and_fire():
    """檢查雙重條件 (體感 + 語音)"""
    global last_gesture_time, last_voice_time, ble_characteristic, current_switch_state
    
    now = time.ticks_ms()
    
    # 檢查兩個動作是否都在最近發生
    if (time.ticks_diff(now, last_gesture_time) < COMBO_WINDOW) and \
       (time.ticks_diff(now, last_voice_time) < COMBO_WINDOW):
        
        print("\n>>> 🔥🔥🔥 [Combo 達成] 執行切換！ 🔥🔥🔥")
        
        if current_switch_state:
            cmd = CMD_CLOSE; txt = "關閉 (OFF)"; nxt = False
        else:
            cmd = CMD_OPEN;  txt = "開啟 (ON)";  nxt = True
            
        print(f"執行：{txt}")
        
        if ble_characteristic:
            try:
                await ble_characteristic.write(cmd, response=False)
                current_switch_state = nxt
                save_current_state(nxt)
                
                # 成功特效
                for _ in range(5): led.toggle(); await asyncio.sleep(0.05)
                led.off()
                
                # 重置時間，避免重複觸發
                last_gesture_time = 0
                last_voice_time = 0
                
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"❌ 發送失敗: {e}")
        else:
            print("⚠️ 藍牙未連線")
            for _ in range(3): led.on(); await asyncio.sleep(0.1); led.off(); await asyncio.sleep(0.1)

async def temp_led_flash():
    """單一訊號提示燈 (亮 1 秒)"""
    led.on()
    await asyncio.sleep(1.0)
    # 如果沒有觸發 Combo 才滅燈
    if (time.ticks_diff(time.ticks_ms(), last_gesture_time) > COMBO_WINDOW) and \
       (time.ticks_diff(time.ticks_ms(), last_voice_time) > COMBO_WINDOW):
        led.off()

# ==========================================
# [3. 任務區]
# ==========================================

async def bluetooth_keeper():
    global ble_connection, ble_characteristic
    print("🚀 [任務] 藍牙守護者啟動...")
    while True:
        if ble_connection is None:
            conn = None
            try:
                device = aioble.Device(aioble.ADDR_PUBLIC, TARGET_ADDR_BYTES)
                conn = await device.connect(timeout_ms=5000)
            except:
                try:
                    device = aioble.Device(aioble.ADDR_RANDOM, TARGET_ADDR_BYTES)
                    conn = await device.connect(timeout_ms=5000)
                except:
                    pass
            if conn:
                try:
                    service = await conn.service(SERVICE_UUID)
                    ble_characteristic = await service.characteristic(CHAR_UUID)
                    ble_connection = conn
                    print("✅ 藍牙已連線")
                    led.on(); await asyncio.sleep(1); led.off()
                except:
                    await conn.disconnect()
            await asyncio.sleep(5)
        else:
            try:
                await ble_connection.disconnected()
                ble_connection = None; ble_characteristic = None
                print("⚠️ 藍牙斷線")
            except:
                pass
        await asyncio.sleep(1)

# --- 體感偵測 (純 X 軸) ---
async def gesture_loop():
    global last_gesture_time
    print("🥋 [任務] 體感偵測 (純 X 軸判定)")
    is_armed = False; action_started = False; last_time = 0
    
    while True:
        # 只讀 X
        x = adc_x.read_u16()
        pose = get_x_pose(x)
        now = time.ticks_ms()
        
        # 邏輯：必須先在上 (UP)，然後往下 (DOWN)，再回到上 (UP) 
        # 或者簡單一點：只要有明顯的 下降 再 回升 即可
        
        if pose == "UP":
            if action_started:
                # 動作完成：下 -> 上
                print(f"🥋 [體感 OK] 數值變化 > 1800 (目前:{x})")
                last_gesture_time = now
                asyncio.create_task(temp_led_flash())
                await check_and_fire()
                
                action_started = False; is_armed = True
            
            if not is_armed: is_armed = True

        elif pose == "DOWN":
            # 數值掉到 15000 以下
            if is_armed and not action_started:
                action_started = True; last_time = now
        
        else: # MID 狀態
            pass # 過渡區，不動作

        # 超時
        if action_started and (now - last_time > GESTURE_TIMEOUT):
            action_started = False; is_armed = False

        await asyncio.sleep(0.05)

# --- 語音偵測 ---
async def voice_command_loop():
    global last_voice_time
    print("🎤 [任務] 語音偵測 (隨時待命)")
    
    while True:
        if pin_mic.value() == 1:
            await asyncio.sleep(0.2)
            while pin_mic.value() == 1: await asyncio.sleep(0.05)

            start_wait = time.ticks_ms()
            got_second = False
            while (time.ticks_ms() - start_wait) < 800:
                if pin_mic.value() == 1:
                    got_second = True; break
                await asyncio.sleep(0.01)
            
            if got_second:
                print("🎤 [語音 OK] 口令確認")
                last_voice_time = time.ticks_ms()
                asyncio.create_task(temp_led_flash())
                await check_and_fire()
            else:
                pass 
                
        await asyncio.sleep(0.01)

# ==========================================
# [4. 主程式]
# ==========================================
async def main():
    await asyncio.gather(
        bluetooth_keeper(),
        gesture_loop(),
        voice_command_loop()
    )

asyncio.run(main())
