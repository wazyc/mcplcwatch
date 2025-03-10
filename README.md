# mcplcwatch

MCプロトコルを使用してPLCのデータを読み書き、または監視するPythonライブラリです。    
A Python library for reading, writing, and monitoring PLC data using MC protocol.

## 機能 | Features

- MCプロトコル経由でPLCのデータを読み書き  
  Read and write PLC data via MC protocol
- 3Eフレーム、4Eフレームをサポート  
  Support for 3E and 4E frames
- デバイスタイプ（D, X, Y, M, SM, SD, Wなど）に対応  
  Support for various device types (D, X, Y, M, SM, SD, W, etc.)
- イベント駆動型の監視機能  
  Event-driven monitoring functionality

## インストール方法 | Installation

```bash
pip install mcplcwatch
```

## 使用例 | Usage Examples

### 基本的な読み書き | Basic Reading and Writing

```python
from mcplcwatch import PlcClient

# PLCに接続 (デフォルトは3Eフレーム)
# Connect to PLC (default is 3E frame)
plc = PlcClient(host="192.168.10.130", port=5000)

# データの読み取り
# Read data
d_values = plc.read_devices("D", 100, 10)  # D100からD109まで10点読み取り / Read 10 points from D100 to D109
print(d_values)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# データの書き込み
# Write data
plc.write_device("D", 100, 999)  # D100に999を書き込み / Write 999 to D100
plc.write_devices("D", 110, [1, 2, 3, 4, 5])  # D110からD114に連続して値を書き込み / Write values sequentially from D110 to D114

# 文字列の書き込み
# Write a string
plc.write_string("D", 200, "Hello PLC")

# 接続を閉じる
# Close the connection
plc.close()
```

### 4Eフレームの使用方法 | Using 4E Frame

```python
from mcplcwatch import PlcClient, MCProtocol

# 4Eフレームでの接続
# Connect using 4E frame
plc = PlcClient(
    host="192.168.10.130",
    port=5000,
    frame_type=MCProtocol.FRAME_4E,
    network_no=0,  # ネットワーク番号 / Network number
    pc_no=0xFF,    # PC番号 / PC number
    unit_io=0x03FF,  # ユニットI/O番号 / Unit I/O number
    unit_station=0,  # ユニット局番号 / Unit station number
)

# 以降は3Eフレームと同じように使用できます
# Can be used in the same way as 3E frame from here on
d_values = plc.read_devices("D", 100, 10)
plc.write_device("D", 100, 999)
plc.close()
```

### データの監視 | Data Monitoring

```python
from mcplcwatch import PlcClient, PlcMonitor

# PLCに接続
# Connect to PLC
plc = PlcClient(host="192.168.10.130", port=5000)

# モニターの設定
# Set up monitor
monitor = PlcMonitor(plc)

# コールバック関数の定義
# Define callback function
def on_change(device_type, device_number, old_value, new_value):
    print(f"{device_type}{device_number} changed from {old_value} to {new_value}")

# 監視の開始
# Start monitoring
monitor.add_device("D", 100, callback=on_change)
monitor.add_devices("M", 0, 10, callback=on_change)  # M0からM9まで10点監視 / Monitor 10 points from M0 to M9
monitor.start(interval=1.0)  # 1秒間隔で監視 / Monitor at 1-second intervals

# メインプログラム
# Main program
try:
    while True:
        # メインプログラムの処理
        # Main program processing
        pass
except KeyboardInterrupt:
    # 監視を停止
    # Stop monitoring
    monitor.stop()
    plc.close()
```

## 対応デバイス | Supported Devices

- D: データレジスタ / Data register
- X: 入力リレー / Input relay
- Y: 出力リレー / Output relay
- M: 内部リレー / Internal relay
- SM: 特殊リレー / Special relay
- SD: 特殊レジスタ / Special register
- W: リンクレジスタ / Link register
- その他多数のデバイスに対応 / And many other devices

## フレームタイプの選択 | Selecting Frame Type

このライブラリでは、以下のMCプロトコルフレームタイプをサポートしています：  
This library supports the following MC protocol frame types:

- **3Eフレーム**: デフォルトのフレームタイプ。最も一般的に使用されます。  
  **3E Frame**: The default frame type. Most commonly used.
- **4Eフレーム**: 複数のネットワークやCPUを経由する場合に使用されます。  
  **4E Frame**: Used when communicating through multiple networks or CPUs.

フレームタイプの選択は、PLCの設定や接続環境によって異なります。一般的に、単一のPLCに直接接続する場合は3Eフレーム、
複数のネットワークを経由する場合やGOT経由でPLCに接続する場合は4Eフレームを使用します。  
The choice of frame type depends on the PLC configuration and connection environment. Generally, 3E frame is used when connecting directly to a single PLC, while 4E frame is used when connecting through multiple networks or through a GOT.

## ライセンス | License

MIT License

## 貢献 | Contributing

バグ報告や機能リクエストは、Githubのイシューでお願いします。
プルリクエストも歓迎します。  
Bug reports and feature requests are welcome on Github issues.
Pull requests are also welcome. 