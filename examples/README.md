# mcplcwatch サンプル集 (mcplcwatch Samples)

このディレクトリには、mcplcwatchライブラリの使用方法を示すサンプルプログラムが含まれています。
This directory contains sample programs demonstrating how to use the mcplcwatch library.

## サンプル一覧 (List of Samples)

### 1. 基本的な読み書き (Basic Reading and Writing)
**ファイル (File):** `basic_read_write.py`

PLCデバイスからの基本的なデータの読み書き方法を示します。
Demonstrates basic reading and writing of data from PLC devices.

```bash
python examples/basic_read_write.py
```

### 2. 監視機能の例 (Monitoring Example)
**ファイル (File):** `monitor_example.py`

PLCデバイスの値を監視し、変更があった場合にコールバック関数を呼び出す方法を示します。
Demonstrates how to monitor PLC device values and call callback functions when they change.

```bash
python examples/monitor_example.py
```

### 3. フレームタイプ指定の例 (Frame Type Example)
**ファイル (File):** `frame_type_example.py`

3Eフレームと4Eフレームの両方のフレームタイプを使用する方法を示します。
Demonstrates how to use both 3E frame and 4E frame types.

```bash
python examples/frame_type_example.py
```

### 4. 複数PLCの同時監視 (Monitoring Multiple PLCs Simultaneously)
**ファイル (File):** `multi_plc_monitor.py`

異なるIPアドレスを持つ複数のPLCに接続し、それぞれのPLCの異なるデバイスを同時に監視する方法を示します。
Demonstrates how to connect to multiple PLCs with different IP addresses and monitor different devices of each PLC simultaneously.

```bash
python examples/multi_plc_monitor.py
```

## 使用方法 (Usage)

各サンプルファイルは、PLCのIPアドレスや監視するデバイスなどの設定を変更して、実際の環境に合わせて調整することができます。
Each sample file can be modified by changing settings such as the PLC's IP address and devices to monitor to suit your actual environment.

サンプルを実行する前に、以下を確認してください：
Before running the samples, please check the following:

1. mcplcwatchライブラリがインストールされていること
   mcplcwatch library is installed
   
2. 実際のPLCのIPアドレスとポート番号を設定していること
   Set the actual IP address and port number of your PLC
   
3. 監視するデバイスが実際のPLCに存在すること
   The devices to be monitored exist in the actual PLC

## 注意事項 (Notes)

- これらのサンプルはデモンストレーション目的のものです。実際のプロジェクトでは、より堅牢なエラー処理とセキュリティ対策を実装してください。
  These samples are for demonstration purposes. In actual projects, implement more robust error handling and security measures.
  
- 実際のPLC環境で実行する場合は、適切なネットワーク設定とセキュリティ対策を行ってください。
  When running in actual PLC environments, please implement appropriate network settings and security measures. 