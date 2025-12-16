import uasyncio as asyncio
import aioble
import bluetooth
import machine
import ubinascii

# --- 你的裝置資料 ---
TARGET_ADDR_STR = "E4:66:E5:8E:2E:97"

# UUID 設定 (根據你上次提供的)
SERVICE_UUID = bluetooth.UUID(0xFFF0) 
CHAR_UUID = bluetooth.UUID(0xFFF2)

# 指令
CMD_CLOSE = bytes([0x43, 0x02, 0x01, 0x01])
CMD_OPEN = bytes([0x43, 0x02, 0x01, 0x02])

led = machine.Pin('LED', machine.Pin.OUT)

async def direct_connect():
    print("🚀 啟動「狙擊手模式」 (跳過掃描，直接連線)...")
    
    # 將 MAC 字串轉為 bytes
    target_addr_bytes = ubinascii.unhexlify(TARGET_ADDR_STR.replace(":", ""))
    
    device = None
    connection = None
    
    # --- 嘗試 1: 假設它是 Public Address (大部分市售產品) ---
    print(f"👉 嘗試模式 A (Public Address): {TARGET_ADDR_STR}")
    try:
        # 這裡不掃描，直接建立裝置物件
        device = aioble.Device(aioble.ADDR_PUBLIC, target_addr_bytes)
        print("   正在敲門...")
        connection = await device.connect(timeout_ms=5000)
        print("✅ 模式 A 連線成功！")
    except Exception as e:
        print(f"❌ 模式 A 失敗: {e}")

    # --- 嘗試 2: 如果 A 失敗，假設它是 Random Address ---
    if not connection:
        print(f"👉 嘗試模式 B (Random Address): {TARGET_ADDR_STR}")
        try:
            device = aioble.Device(aioble.ADDR_RANDOM, target_addr_bytes)
            print("   正在敲門...")
            connection = await device.connect(timeout_ms=5000)
            print("✅ 模式 B 連線成功！")
        except Exception as e:
            print(f"❌ 模式 B 失敗: {e}")

    # --- 如果連線成功，發送指令 ---
    if connection:
        print("🔗 建立服務連結中...")
        try:
            service = await connection.service(SERVICE_UUID)
            char = await service.characteristic(CHAR_UUID)
            
            print(f"📤 發送開關指令...")
            await char.write(CMD_OPEN, response=False)
            print("✨✨✨ 成功發射訊號！(LED 快閃) ✨✨✨")
            
            # 成功特效
            for _ in range(10):
                led.toggle()
                await asyncio.sleep(0.05)
                
            await connection.disconnect()
            print("👋 任務完成，斷開連線")
            
        except Exception as e:
            print(f"⚠️ 服務/特徵錯誤: {e}")
            print("可能 UUID 還是不對，請用手機 App (nRF Connect) 確認")
            await connection.disconnect()
    else:
        print("💀 兩種模式都連不上。")
        print("請確認：1. 手機藍牙已關閉  2. 裝置有電  3. 距離夠近")

# 執行
asyncio.run(direct_connect())