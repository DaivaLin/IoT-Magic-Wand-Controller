# 🪄 IoT Magic Wand: Wireless Gesture Control for Smart Lights
![Project Banner](./images/project_banner.jpg)

## 📖 Introduction (專案介紹)
本專案旨在利用物聯網技術解決傳統開關需要「走過去按」的不便。透過 **Raspberry Pi Pico 2 W** 結合 **ADXL335 三軸加速度計**，我們製作了一款「無線手勢控制器」。使用者只需揮動裝置（例如：向左揮、向右揮），Pico 2 W 即可透過藍牙 (BLE) 發送指令控制 **Sanqi 智慧藍牙開關**，實現類似「魔法棒」的非接觸式家電控制。

**主要功能：**
* **無線運作**：結合鋰電池擴充板，擺脫 USB 線材束縛。
* **手勢辨識**：解析類比加速度訊號，判斷特定動作。
* **藍牙控制**：取代手機 App，直接由開發板對藍牙開關進行寫入操作。

## 🎥 Demo Video (展示影片)
請點擊下方連結觀看專案運作影片：
[![Watch the video](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)
## 🛠️ Hardware Requirements (硬體需求)

| Component | Description | Function |
| :--- | :--- | :--- |
| **Microcontroller** | Raspberry Pi Pico 2 W | 核心控制器，採用 RP2350 晶片，內建 Wi-Fi 與 Bluetooth 5.2。 |
| **Power Supply** | Pico UPS / Battery Expansion Board | 提供電源，背面搭載 18650 鋰電池 (2000mAh)，實現無線移動。 |
| **Sensor** | GY-61 (ADXL335) | 三軸加速度模組 (Analog Output)，用來偵測揮動姿勢。 |
| **Actuator** | Sanqi Smart Light Switch (x2) | 藍牙遙控開關，接收 BLE 指令進行開/關燈。 |
| **Others** | Jumper Wires, Micro USB Cable | 連接線材與燒錄用線。 |

## 🔌 Circuit Diagram & Wiring (電路圖與接線)

### 接線說明 (Wiring Pinout)
由於 ADXL335 是類比輸出，我們使用 Pico 的 ADC 引腳進行讀取：

* **GY-61 (ADXL335) to Pico 2 W:**
    * `VCC` -> `3.3V (OUT)`
    * `GND` -> `GND`
    * `X-OUT` -> `GP26 (ADC0)`
    * `Y-OUT` -> `GP27 (ADC1)`
    * `Z-OUT` -> `GP28 (ADC2)`

### 示意圖 (Schematic)
![Circuit Diagram](./images/circuit_diagram.png)

### 實體照片 (Hardware Mockup)
![Wiring Photo](./images/wiring_photo.jpg)

---

## 📡 Bluetooth Protocol Analysis (藍牙協定分析)
為了讓 Pico 能控制市售的藍牙開關，我們需要先找出開關的 **MAC Address** 以及控制指令的 **Payload (封包內容)**。以下是逆向工程的完整步驟。

### Step 1: 掃描與定位設備 (Device Discovery)
使用 Raspberry Pi 的 `bluetoothctl` 工具進行掃描。為了避免環境中大量雜訊，我們設定了濾鏡只掃描 BLE 訊號。

```bash
# 在 Terminal 執行 bluetoothctl
scan off
menu scan
clear              # 清除舊濾鏡
transport le       # 只掃描 BLE (避免 BR/EDR 混入)
duplicate-data off # 避免重複顯示同一裝置的廣播
back
scan on
```

經過約 10-20 秒掃描，我們找到了目標設備地址：
> **Target MAC:** `E4:66:E5:8E:2E:97`

### Step 2: 探索 GATT 服務 (GATT Exploration)
連線並尋找可寫入的特徵值 (Characteristic)。

```bash
# 連線到目標裝置
connect E4:66:E5:8E:2E:97

# 進入 GATT 選單列出屬性
menu gatt
list-attributes
```

經過測試與屬性查詢 (`attribute-info`)，我們確認了關鍵通道：
* **Notify (接收通知/狀態回傳):** `0000fff1-0000-1000-8000-00805f9b34fb`
* **Write (寫入指令/控制):** `0000fff2-0000-1000-8000-00805f9b34fb` (Handle: 0x0025)

### Step 3: 擷取控制封包 (Packet Sniffing)
由於直接寫入 ASCII 字串 (如 "HELLO") 無效，我們必須攔截官方 App 發出的原始 Hex Code。

**操作步驟 (使用 Android OPPO 工程模式):**
1. 打開撥號介面輸入 `*#800#` 進入反饋工具箱。
2. 選擇 **Bluetooth** -> 開啟 **Bluetooth HCI Log**。
3. 點擊「開始抓取」，切換飛航模式重置藍牙，然後打開 App 操作「開燈」與「關燈」。
4. 停止抓取並匯出 `btsnoop_hci` 或 `.cfa` 日誌檔。
   <img width="926" height="110" alt="image" src="https://github.com/user-attachments/assets/e456a88a-a605-481c-ab5c-8178a949fc51" />


### Step 4: Wireshark 分析
將日誌檔匯入 Wireshark，並使用以下過濾器尋找寫入指令：
`btatt.opcode == 0x52 || btatt.opcode == 0x12`

* `0x52`: Write Command (無須回覆)
* `0x12`: Write Request (需要回覆)

<img width="1304" height="687" alt="image" src="https://github.com/user-attachments/assets/8b2e71bf-c815-418f-a1a3-0b11cb7f41bb" />


**分析結果：**
我們在 Payload 中找到了控制開關的關鍵 Hex Code：
* **開燈指令:** `0x43 0x02 0x01 0x01`
* **關燈指令:** `0x43 0x02 0x01 0x02`
<img width="980" height="973" alt="image" src="https://github.com/user-attachments/assets/40f54809-ccea-431a-aad0-875d099b5cca" />

**最終結果：**
```bash
select-attribute /org/bluez/hci0/dev_E4_66_E5_8E_2E_97/service0021/char0025
# 開
write "0x43 0x02 0x01 0x01"
# 關
write "0x43 0x02 0x01 0x02"
```

---

## 💻 Software & Implementation (軟體實作)

### 開發環境
* **Language:** MicroPython
* **IDE:** Thonny IDE
* **Libraries:** `aioble`, `bluetooth`, `machine`

### 核心邏輯
程式碼運作流程如下：
1.  **初始化**：啟動 BLE Central 模式，掃描目標藍牙開關的 MAC Address。
2.  **數據讀取**：迴圈讀取 ADXL335 的 X, Y, Z 軸電壓值。
3.  **手勢判斷**：
    * 若 X 軸數值瞬間變化超過閥值 -> 判定為「動作 A」 -> 控制開關 1。
    * 若 Y 軸數值瞬間變化超過閥值 -> 判定為「動作 B」 -> 控制開關 2。
4.  **發送指令**：透過 BLE Characteristic 寫入對應指令。
    * 偵測到 **"晃一下再點一下"** -> 寫入開燈
    * 偵測到 **"點兩下"** -> 寫入關燈


### Source Code (原始碼)
以下是核心程式碼片段 (完整程式碼請見 `src/main.py`)：
```python
import bluetooth
import aioble
import struct

# 定義目標 UUID
_WRITE_CHAR_UUID = bluetooth.UUID("0000fff2-0000-1000-8000-00805f9b34fb")

async def main():
    # 連接設備
    connection = await aioble.device.connect(device_address)
    service = await connection.service(_SERVICE_UUID)
    char = await service.characteristic(_WRITE_CHAR_UUID)
    
    # 寫入指令範例 (開燈)
    command = bytes([0x43, 0x02, 0x01, 0x01])
    await char.write(command)
```
*(完整程式碼請見 Repository 中的 `src/main.py`)*

## 🚀 Usage Instructions (操作說明)
1.  **準備硬體**：將 Pico 插上 UPS 底板並確認電池有電。
2.  **上傳程式**：使用 Thonny 將 `main.py` 存入 Pico。
3.  **操作**：手持裝置做出指定動作，觀察智慧開關反應。

## 📚 References (參考資料)
1. **Raspberry Pi Pico 2 W Datasheet**: [Link](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
2. **How to get the Bluetooth Host Controller Interface logs from a modern Android phone** : [Link](https://medium.com/%40charlie.d.anderson/how-to-get-the-bluetooth-host-controller-interface-logs-from-a-modern-android-phone-d23bde00b9fa)
