"""
monitor_example.py - mcplcwatchライブラリのデバイス監視機能を示すサンプルスクリプト
monitor_example.py - Sample script demonstrating device monitoring functionality of the mcplcwatch library

本スクリプトは、mcplcwatchライブラリを使用して、PLCのデバイスデータを監視する方法を示しています。
This script demonstrates how to monitor PLC device data using the mcplcwatch library.
"""

import sys
import time
import signal
import logging
from mcplcwatch import PlcClient, PlcMonitor, PlcError

# ロギングの設定 (Logging configuration)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def on_device_change(device_type, device_number, old_value, new_value):
    """
    デバイス値変化時のコールバック関数
    Callback function for device value changes
    
    引数 (Arguments):
        device_type (str): デバイスタイプ (Device type)
        device_number (int): デバイス番号 (Device number)
        old_value: 変更前の値 (Value before change)
        new_value: 変更後の値 (Value after change)
    """
    logger.info(f"{device_type}{device_number} changed from {old_value} to {new_value}")


def on_device_error(device_type, device_number, error):
    """
    デバイス監視エラー時のコールバック関数
    Callback function for device monitoring errors
    
    引数 (Arguments):
        device_type (str): デバイスタイプ (Device type)
        device_number (int): デバイス番号 (Device number)
        error: 発生したエラー (Error that occurred)
    """
    logger.error(f"Error occurred while monitoring {device_type}{device_number}: {error}")


def main():
    """
    メイン関数
    Main function
    """
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <PLC_IP> <PLC_PORT>")
        print("Example: python monitor_example.py 192.168.10.10 5000")
        return
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    # シグナルハンドラの設定（Ctrl+Cで終了） (Set signal handler (exit with Ctrl+C))
    stop_event = False
    
    def signal_handler(sig, frame):
        nonlocal stop_event
        logger.info("Received exit signal. Exiting...")
        stop_event = True
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # PLCに接続 (Connect to PLC)
        logger.info(f"Connecting to PLC: {host}:{port}")
        plc = PlcClient(host=host, port=port, timeout=2.0)
        
        # モニターの設定 (Configure monitor)
        logger.info("Setting up monitor...")
        monitor = PlcMonitor(plc, interval=0.3)
        
        # 監視対象デバイスの追加 (Add target devices for monitoring)
        # 単一デバイスの監視 (Monitor a single device)
        monitor.add_device('D', 100, callback=on_device_change, on_error=on_device_error)
        
        # 複数デバイスの監視 (Monitor multiple devices)
        monitor.add_devices('D', 200, 5, callback=on_device_change, on_error=on_device_error)
        
        # ビットデバイスの監視 (Monitor bit devices)
        monitor.add_devices('M', 100, 8, callback=on_device_change, on_error=on_device_error)
        
        # 監視開始 (Start monitoring)
        logger.info("Starting monitoring...")
        monitor.start()
        
        # 監視継続 (Continue monitoring)
        logger.info("Press Ctrl+C to exit")
        
        try:
            # 初期値を表示 (Display initial values)
            d100 = plc.read_device('D', 100)
            logger.info(f"D100 initial value: {d100}")
            
            d_values = plc.read_devices('D', 200, 5)
            for i, value in enumerate(d_values):
                logger.info(f"D{200 + i} initial value: {value}")
            
            m_values = plc.read_devices('M', 100, 8)
            for i, value in enumerate(m_values):
                logger.info(f"M{100 + i} initial value: {value}")
        except PlcError as e:
            logger.error(f"Failed to read initial values: {e}")
        
        # 監視処理のメインループ (Main loop for monitoring process)
        while not stop_event:
            # ここに必要な処理を追加 (Add necessary processing here)
            # 例: 別のデバイスの読み書きなど (Example: Reading and writing other devices)
            
            time.sleep(0.1)  # CPU負荷軽減のためのスリープ (Sleep to reduce CPU load)
        
    except PlcError as e:
        logger.error(f"PLC error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # 監視を停止 (Stop monitoring)
        if 'monitor' in locals() and monitor.is_running():
            logger.info("Stopping monitoring...")
            monitor.stop()
        
        # 接続を閉じる (Close connection)
        if 'plc' in locals():
            logger.info("Closing connection to PLC")
            plc.close()


if __name__ == "__main__":
    main() 