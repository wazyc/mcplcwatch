#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
複数のPLCを同時に監視するサンプルプログラム
Sample program to monitor multiple PLCs simultaneously

このサンプルでは、異なるIPアドレスを持つ複数のPLCに接続し、
それぞれのPLCの異なるデバイスを同時に監視する方法を示します。

This sample demonstrates how to connect to multiple PLCs with different IP addresses
and monitor different devices of each PLC simultaneously.
"""

import time
import logging
import sys
import signal
from mcplcwatch.client import PlcClient
from mcplcwatch.monitor import PlcMonitor
from mcplcwatch.error import PlcError

# ロギング設定 (Logging configuration)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PLC接続情報 (PLC connection information)
PLC_CONFIGS = [
    {
        'name': 'PLC1',
        'host': '192.168.1.10',  # PLC1のIPアドレス (IP address of PLC1)
        'port': 5007,            # PLC1のポート番号 (Port number of PLC1)
        'devices': [
            {'type': 'D', 'number': 100, 'count': 10},  # D100からD109までの10ワードを監視 (Monitor 10 words from D100 to D109)
            {'type': 'M', 'number': 0, 'count': 8}      # M0からM7までの8ビットを監視 (Monitor 8 bits from M0 to M7)
        ]
    },
    {
        'name': 'PLC2',
        'host': '192.168.1.20',  # PLC2のIPアドレス (IP address of PLC2)
        'port': 5007,            # PLC2のポート番号 (Port number of PLC2)
        'devices': [
            {'type': 'D', 'number': 200, 'count': 5},   # D200からD204までの5ワードを監視 (Monitor 5 words from D200 to D204)
            {'type': 'X', 'number': 0, 'count': 16}     # X0からX15までの16ビットを監視 (Monitor 16 bits from X0 to X15)
        ]
    }
]

# 実際に接続する際には、実在するPLCのIPアドレスとポート番号に変更してください
# When actually connecting, please change to the IP address and port number of an existing PLC


# 値変更時のコールバック関数 (Callback function for value changes)
def on_value_changed(plc_name, device_type, device_number, old_value, new_value):
    """
    値が変化した場合に呼び出されるコールバック関数
    Callback function called when a value changes
    
    引数 (Arguments):
        plc_name (str): PLC名 (PLC name)
        device_type (str): デバイスタイプ (Device type)
        device_number (int): デバイス番号 (Device number)
        old_value: 変更前の値 (Value before change)
        new_value: 変更後の値 (Value after change)
    """
    logger.info(f"{plc_name}: {device_type}{device_number} value changed: {old_value} -> {new_value}")


# エラー発生時のコールバック関数 (Callback function for errors)
def on_error(plc_name, device_info, error):
    """
    エラーが発生した場合に呼び出されるコールバック関数
    Callback function called when an error occurs
    
    引数 (Arguments):
        plc_name (str): PLC名 (PLC name)
        device_info: デバイス情報 (Device information)
        error: 発生したエラー (Error that occurred)
    """
    logger.error(f"{plc_name}: {device_info} error occurred: {error}")


def create_monitor_for_plc(plc_config):
    """
    PLC用のモニターを作成する
    Create a monitor for a PLC
    
    引数 (Arguments):
        plc_config (dict): PLC設定 (PLC configuration)
        
    戻り値 (Returns):
        PlcMonitor: 作成されたモニター (Created monitor)
    """
    plc_name = plc_config['name']
    host = plc_config['host']
    port = plc_config['port']
    
    try:
        # PLCクライアントの作成 (Create PLC client)
        plc_client = PlcClient(host=host, port=port)
        
        # モニターの作成 (Create monitor)
        plc_monitor = PlcMonitor(plc_client=plc_client, interval=1.0)
        
        # 監視デバイスの追加 (Add monitoring devices)
        for device_config in plc_config['devices']:
            device_type = device_config['type']
            device_number = device_config['number']
            count = device_config['count']
            
            # 単一デバイスの場合 (For single device)
            if count == 1:
                plc_monitor.add_device(
                    device_type=device_type,
                    device_number=device_number,
                    callback=lambda dt, dn, ov, nv, plc=plc_name: on_value_changed(plc, dt, dn, ov, nv),
                    on_error=lambda dt, dn, err, plc=plc_name: on_error(plc, f"{dt}{dn}", err)
                )
                logger.info(f"{plc_name}: Added monitoring for device {device_type}{device_number}")
            # 複数デバイスの場合 (For multiple devices)
            else:
                plc_monitor.add_devices(
                    device_type=device_type,
                    start_number=device_number,
                    count=count,
                    callback=lambda dt, dn, ov, nv, plc=plc_name: on_value_changed(plc, dt, dn, ov, nv),
                    on_error=lambda dt, dn, err, plc=plc_name: on_error(plc, f"{dt}{dn}", err)
                )
                logger.info(f"{plc_name}: Added monitoring for devices {device_type}{device_number}-{device_number + count - 1}")
        
        return plc_monitor
    
    except PlcError as e:
        logger.error(f"{plc_name}: Failed to connect to PLC: {e}")
        return None
    except Exception as e:
        logger.error(f"{plc_name}: Unexpected error occurred: {e}")
        return None


def main():
    """
    メイン関数
    Main function
    """
    # 終了フラグ (Exit flag)
    running = True
    
    # シグナルハンドラの設定 (Set signal handler)
    def signal_handler(sig, frame):
        nonlocal running
        logger.info("Received exit signal. Stopping monitoring...")
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # モニターのリスト (List of monitors)
    monitors = []
    
    try:
        # 各PLCに対してモニターを作成 (Create a monitor for each PLC)
        for plc_config in PLC_CONFIGS:
            monitor = create_monitor_for_plc(plc_config)
            if monitor:
                monitors.append((plc_config['name'], monitor))
        
        if not monitors:
            logger.error("No valid monitors. Exiting.")
            return
        
        # すべてのモニターを開始 (Start all monitors)
        for plc_name, monitor in monitors:
            monitor.start()
            logger.info(f"{plc_name}: Started monitoring")
        
        logger.info("Press Ctrl+C to exit")
        
        # メインループ (Main loop)
        while running:
            time.sleep(1)
        
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
    
    finally:
        # すべてのモニターを停止 (Stop all monitors)
        for plc_name, monitor in monitors:
            if monitor.is_running():
                monitor.stop()
                logger.info(f"{plc_name}: Stopped monitoring")


if __name__ == "__main__":
    main() 