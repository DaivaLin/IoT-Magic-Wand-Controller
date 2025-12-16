# IoT Magic Wand: Wireless Gesture Control for Smart Lights
<img width="300px" alt="image" src="https://github.com/user-attachments/assets/d3f05142-55c0-4600-b6af-2fbce4b26a2b" />


## 📖 Introduction (專案介紹)
本專案旨在利用物聯網技術解決傳統開關需要「走過去按」的不便。透過 **Raspberry Pi Pico 2 W** 高效能雙核心晶片，結合 **ADXL335 三軸加速度計** 與 **高感度聲音模組**，我們製作了一款具備雙重驗證機制的「無線魔法棒」。

使用者只需做出**點頭手勢**（X 軸數值變化）並同時喊出**雙音節口令**（如「開...燈」），Pico 2 W 即會進行邏輯判定，並透過 **藍牙 (BLE)** 直接發送 UUID 指令控制 Sanqi 智慧開關。這種「動口又動手」的設計不僅實現了非接觸式控制，更有效解決了單一感測器容易誤觸的問題。

**主要功能：**
* **無線運作 (Portable Design)**
    * 結合 18650 鋰電池擴充板，擺脫 USB 線材與供電插座的束縛，實現真正的無線隨身控制。

* **體感辨識 (Motion Recognition)**
    * 解析 ADXL335 的類比電壓訊號，透過演算法鎖定 X 軸數值變化。
    * 精準判斷裝置的「上 -> 下 -> 上」點頭動作，排除雜訊干擾。

* **語音雙重驗證 (Dual Authentication)**
    * 引入麥克風模組偵測環境音量節奏。
    * 系統要求「體感動作」與「語音指令」必須在 2.5 秒內同時發生才觸發，大幅降低誤動作機率。

* **藍牙直連 (Direct BLE Control)**
    * 取代傳統手機 App 操作，由 Pico 開發板主動擔任藍牙主機 (Central)。
    * 直接對智慧開關的特徵值 (Characteristic) 進行寫入操作，反應速度快且無需配對密碼。

## 🎥 Demo Video (展示影片)
請點擊下方連結觀看專案運作影片：
[https://youtube.com/shorts/hAkGjmuax0k]
## 🛠️ Hardware Requirements (硬體需求)

| Component | Device / Model | Description | Function & Pin Mapping |
| :--- | :--- | :--- | :--- |
| **Microcontroller** | Raspberry Pi Pico 2 W | 核心控制器，採用 RP2350 晶片，內建 Wi-Fi 與 Bluetooth 5.2。 | **主控核心**<br>負責執行 `aioble` 藍牙連線、ADC 採樣與邏輯判斷 (雙重驗證)。 |
| **Power Supply** | Pico UPS / Expansion Board | 電源擴充板，背面搭載 18650 鋰電池 (2000mAh)，實現無線移動。 | **供電系統**<br>提供穩定的 3.3V 電源，透過並聯方式供給所有感測器。 |
| **Motion Sensor** | GY-61 (ADXL335) | 三軸加速度模組 (Analog Output)，類比輸出。 | **體感偵測 (GP28)**<br>讀取 X 軸數值，偵測「點頭」動作 (數值下降幅度 > 1800)。 |
| **Sound Sensor** | High-Sensitivity Mic (KY-037) | 紅色高感度聲音模組，搭載 LM393 比較器。 | **語音偵測 (GP17)**<br>使用數位輸出 (DO) 偵測雙音節指令 (如「開...燈」)。 |
| **Actuator** | Sanqi Smart Light Switch (x2) | 藍牙遙控開關，接收 BLE 指令進行開/關燈。 | **受控設備**<br>透過 BLE 發送 UUID `FFF2` 指令來切換繼電器狀態。 |
| **Connectivity** | Breadboard / Jumper Wires | 麵包板與杜邦線。 | **線路連接**<br>用於將 Pico 唯一的 3V3 電源分流給多個模組使用。 |

## 🔌 Circuit Diagram & Wiring (電路圖與接線)

### 📝 詳細腳位對照表 (Detailed Pin Mapping Table)

這是施工時最準確的參考依據。由於我們的程式邏輯已簡化為僅偵測 X 軸「點頭」動作，因此移除了 Y 軸的連接。

請務必確保 ADXL335 與麥克風模組的 VCC 都是接在 **3.3V** (透過麵包板分流)，**絕對不可接到 5V**，以免燒毀模組或 Pico GPIO。

| Pico 2 W Pin | Pin Name | 連接目標模組 (Target Module) | 目標腳位名稱 (Target Pin) | 功能說明 (Function) |
| :--- | :--- | :--- | :--- | :--- |
| **Power & GND** | | | | |
| Pin 36 | **3V3(OUT)** | 麵包板紅色軌道 (+) | N/A | **主電源來源**<br>Pico 唯一的 3.3V 輸出，需連接至麵包板供所有模組分流使用。 |
| Pin 38 (或任一 GND) | **GND** | 麵包板藍色軌道 (-) | N/A | **共同接地**<br>連接至麵包板，供所有模組共用。 |
| **訊號連接 (Signal)** | | | | |
| Pin 34 | **GP28** (ADC2) | ADXL335 (GY-61) | **X-OUT** | **體感訊號輸入**<br>讀取 X 軸類比電壓，作為「點頭」動作判定的核心依據。 |
| Pin 22 | **GP17** | Mic (KY-037) | **D0** | **語音訊號輸入**<br>讀取聲音模組的數位 (High/Low) 訊號，偵測雙音節指令。 |
| **懸空腳位 (NC)** | | | | |
| N/A | N/A | ADXL335 (GY-61) | **Y-OUT**, Z-OUT | **不使用**<br>程式已移除 Y 軸判定邏輯，這兩腳位請懸空。 |
| N/A | N/A | Mic (KY-037) | A0 | **不使用**<br>本專案僅使用數位訊號 (D0)，類比腳位懸空。 |

### ⚠️ 施工重要提醒 (Important Construction Notices)

1.  **共用電源的關鍵 (Power Distribution)**
    * Raspberry Pi Pico 2 W 只有一支 **3V3 (Pin 36)** 輸出腳位。
    * **正確接法**：請先將 Pin 36 接到麵包板的 **紅色電源軌 (Red Rail)**，再將 ADXL335 和 KY-037 的 VCC 線插到該軌道上取電。
    * **錯誤接法**：請勿試圖將兩條線硬塞進同一個 Pico 腳位孔，這容易導致接觸不良或短路。

2.  **麥克風靈敏度調校 (Sensitivity Tuning)**
    * 硬體接好後，**必須**使用小螺絲起子調整紅色麥克風模組上的 **藍色方形可變電阻 (Potentiometer)**。
    * **調校目標**：
        * **環境安靜時**：模組上的訊號 LED (Signal LED) 應保持 **熄滅**。
        * **說話或拍手時**：訊號 LED 應隨聲音同步 **閃爍**。
    * *狀況排除*：如果 LED 一直恆亮，代表太靈敏（請逆時針轉）；如果大叫都不亮，代表太遲鈍（請順時針轉）。

3.  **嚴禁連接 5V 電壓 (Voltage Warning)**
    > **🔴 危險警告**：ADXL335 感測器與 Pico 的 GPIO 腳位最高僅能承受 **3.3V**。
    * 請仔細檢查擴充板上的接腳標示，**絕對不要**將感測器的 VCC 接到 `5V`、`VBUS` 或 `VSYS`，否則會瞬間燒毀感測器或是 Pico 的主晶片。

4.  **線路固定 (Wire Securing)**
    * 由於本專案需要進行「揮動」與「點頭」操作，杜邦線極易在晃動過程中鬆脫。
    * **建議**：在測試功能正常後，可使用絕緣膠帶或束帶將杜邦線稍微固定在麵包板或底座上，避免因接觸不良導致數據跳動或系統當機。


### 示意圖 (Schematic)
![Circuit Diagram](./images/circuit_diagram.png)

---

## 📡 Bluetooth Protocol Analysis (藍牙協定分析)
為了讓 Pico 能控制市售的藍牙開關，我們需要先找出開關的 **MAC Address** 以及控制指令的 **Payload (封包內容)**。
APP 內的 **MAC Address** 
<img width="296" height="172" alt="image" src="https://github.com/user-attachments/assets/4635449b-71a7-4f1f-9215-17a157f68be0" />

以下是逆向工程的完整步驟。

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

<img width="700px" alt="image" src="https://github.com/user-attachments/assets/8b2e71bf-c815-418f-a1a3-0b11cb7f41bb" />


**分析結果：**
我們在 Payload 中找到了控制開關的關鍵 Hex Code：
* **開燈指令:** `0x43 0x02 0x01 0x01`
* **關燈指令:** `0x43 0x02 0x01 0x02`
<img width="700px" alt="image" src="https://github.com/user-attachments/assets/40f54809-ccea-431a-aad0-875d099b5cca" />

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

### 🛠️ 開發環境 (Development Environment)
* **Language:** MicroPython (非同步架構 / Asynchronous)
* **IDE:** Thonny IDE
* **Libraries:** `uasyncio`, `aioble`, `bluetooth`, `machine`, `ubinascii`

### ⚙️ 核心邏輯 (Core Logic)

本系統採用 **`uasyncio` 非同步多工架構**，同時執行藍牙連線維持、體感偵測與語音監聽三大任務。

1.  **初始化與狀態記憶 (Initialization & State Memory)**
    * 系統啟動時讀取 `state.txt` 檔案，恢復上次的開關狀態 (ON/OFF)。
    * 跳過傳統掃描，直接針對目標 MAC Address (`E4:66...`) 建立藍牙連線 (Blind Connect)。

2.  **多工感測任務 (Multitasking Sensing)**
    * **體感偵測 (Gesture Task)**：
        * 持續取樣 ADXL335 的 **X 軸**數值。
        * 當數值瞬間下降超過閥值 (Delta > 1800)，判定為「點頭動作 (Nod)」。
    * **語音偵測 (Voice Task)**：
        * 監聽 KY-037 麥克風數位訊號。
        * 辨識 **雙音節節奏** (如「開...燈」)，過濾單一雜訊。

3.  **雙重驗證判定 (Dual Authentication / Combo)**
    * 系統維護一個 **2.5 秒的時間窗口 (Time Window)**。
    * **觸發條件**：必須在窗口內同時偵測到「體感動作」與「語音指令」（不分先後順序）。
    * 此機制可有效防止單一感測器誤判（如走路震動或關門聲）。

4.  **指令發送與狀態切換 (Action & Toggle)**
    * 一旦 Combo 達成，系統根據目前記憶狀態進行 **反向切換 (Toggle)**：
        * 若目前為 ON $\rightarrow$ 發送 OFF 指令 $\rightarrow$ 寫入 `state.txt`。
        * 若目前為 OFF $\rightarrow$ 發送 ON 指令 $\rightarrow$ 寫入 `state.txt`。
    * 透過 BLE Characteristic (`FFF2`) 寫入 Hex 指令完成控制。

### 📂 Project File Structure (專案檔案結構)

| File Name | Category | Function & Purpose |
| :--- | :--- | :--- |
| **main.py** | Core Application (核心主程式) | **專案大腦**。整合藍牙 (aioble)、體感 (X軸)、聲控 (雙音節) 與多工處理，執行「揮動 + 咒語」的組合觸發邏輯。 |
| **boot.py** | System Boot (開機引導) | **無線後門**。開機時優先執行，負責連線 Wi-Fi 並啟動 WebREPL，讓你能透過無線網路更新程式，無需插 USB 線。 |
| **webrepl_cfg.py** | Configuration (系統設定) | **安全憑證**。儲存 WebREPL 的登入密碼 (代碼中預設為 `1234`)，保護你的無線除錯通道。 |
| **data_logger.py** | Analysis Tool (數據採集) | **黑盒子**。高速錄製 ADXL335 數據並存成檔案，用於匯出至 Excel 分析動作波形與計算閾值 (Threshold)。 |
| **gesture_algo_test.py** | Testing (演算法驗證) | **體感實驗室**。獨立測試「上 → 下 → 上」的揮動邏輯，排除藍牙干擾，單純驗證手勢靈敏度。 |
| **mic_hardware_check.py** | Testing (硬體校正) | **聽力檢查**。讀取麥克風數位訊號，用 LED 即時顯示聲音偵測狀態，輔助調整模組上的藍色旋鈕。 |
| **ble_connectivity_test.py** | Testing (通訊測試) | **藍牙狙擊槍**。跳過感測器邏輯，直接嘗試連線並切換開關，用於快速排除藍牙 MAC 位址或 UUID 設定錯誤。 |


## 📚 References (參考資料)
1. **Raspberry Pi Pico 2 W Datasheet**: [Link](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
2. **How to get the Bluetooth Host Controller Interface logs from a modern Android phone** : [Link](https://medium.com/%40charlie.d.anderson/how-to-get-the-bluetooth-host-controller-interface-logs-from-a-modern-android-phone-d23bde00b9fa)
