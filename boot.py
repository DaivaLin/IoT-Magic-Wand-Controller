# boot.py - 開機自動執行
import network
import time
import webrepl

# 1. 連線 Wi-Fi
ssid = '你的WiFi名稱'
password = '你的WiFi密碼'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# 等待連線 (最多等 10 秒)
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    time.sleep(1)

# 2. 啟動 WebREPL (無線終端機)
if wlan.status() == 3:
    print('Wi-Fi 連線成功!')
    print('WebREPL IP:', wlan.ifconfig()[0])
    webrepl.start()
else:
    print('Wi-Fi 連線失敗')