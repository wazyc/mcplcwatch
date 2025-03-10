"""
main.py - mcplcwatchライブラリの基本的な使用例を示すメインスクリプト
main.py - Main script showing basic usage examples of the mcplcwatch library

本スクリプトは、mcplcwatchライブラリの基本的な使用方法を示すシンプルな例です。
より詳細な使用例は、examplesディレクトリを参照してください。

This script is a simple example showing the basic usage of the mcplcwatch library.
For more detailed examples, please refer to the examples directory.
"""

import time
import logging
from mcplcwatch import PlcClient, PlcMonitor, PlcError


# ロギングの設定 (Logging configuration)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def on_change(device_type, device_number, old_value, new_value):
    """
    デバイス値変化時のコールバック関数
    Callback function for device value changes
    
    引数 (Arguments):
        device_type (str): デバイスタイプ (Device type)
        device_number (int): デバイス番号 (Device number)
        old_value: 変更前の値 (Value before change)
        new_value: 変更後の値 (Value after change)
    """
    logger.info(f"{device_type}{device_number} changed from {old_value} to {new_value} ({device_type}{device_number} が {old_value} から {new_value} に変更されました)")


def main():
    """
    メイン関数
    Main function
    """
    # PLC接続情報 (PLC connection information)
    host = "192.168.10.130"
    port = 2000
    
    try:
        # PLCに接続 (Connect to PLC)
        logger.info(f"Connecting to PLC: {host}:{port} (PLCに接続します)")
        plc = PlcClient(host=host, port=port, timeout=2.0)
        
        # データの読み取り (Reading data)
        device_type = 'D'
        device_number = 5000
        element = 25
        
        logger.info(f"Reading {element} points of data from {device_type}{device_number} ({device_type}{device_number} から {element}点のデータを読み取ります)")
        result = plc.read_devices(device_type, device_number, element)
        
        # 結果表示 (Displaying results)
        for i, value in enumerate(result):
            logger.info(f"{device_type}{device_number + i}: {value}")
        
        # 監視設定 (Monitoring setup)
        logger.info("Running monitoring example... (監視機能の例を実行します...)")
        
        # モニターの作成 (Creating monitor)
        monitor = PlcMonitor(plc, interval=1.0)
        
        # 監視対象の追加 (Adding monitoring target)
        monitor.add_device('D', 5000, callback=on_change)
        
        # 監視開始 (Start monitoring)
        logger.info("Starting monitoring (for 5 seconds)... (監視を開始します（5秒間）...)")
        monitor.start()
        
        # 5秒間待機 (Wait for 5 seconds)
        time.sleep(5)
        
        # 監視停止 (Stop monitoring)
        logger.info("Stopping monitoring... (監視を停止します...)")
        monitor.stop()
        
    except PlcError as e:
        logger.error(f"PLC error: {e} (PLCエラー)")
    except Exception as e:
        logger.error(f"Unexpected error: {e} (予期しないエラー)")
    finally:
        # 接続を閉じる (Close connection)
        if 'plc' in locals():
            logger.info("Closing connection to PLC (PLCとの接続を閉じます)")
            plc.close()


if __name__ == "__main__":
    main() 