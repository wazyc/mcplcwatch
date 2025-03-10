"""
frame_type_example.py - mcplcwatchライブラリの3E/4Eフレーム使用例を示すサンプルスクリプト
frame_type_example.py - Sample script demonstrating 3E/4E frame usage with the mcplcwatch library

本スクリプトは、mcplcwatchライブラリを使用して、3Eフレームと4Eフレームの両方でPLCと通信する方法を示しています。
This script demonstrates how to communicate with PLCs using both 3E and 4E frames with the mcplcwatch library.
"""

import sys
import time
import logging
from mcplcwatch import PlcClient, MCProtocol, PlcError, PlcCommunicationError

# ロギングの設定 (Logging configuration)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def connect_with_3e_frame(host, port):
    """
    3Eフレームを使用してPLCに接続するサンプル
    Sample of connecting to PLC using 3E frame
    
    引数 (Arguments):
        host (str): PLCのホスト名またはIPアドレス (PLC hostname or IP address)
        port (int): PLCのポート番号 (PLC port number)
        
    戻り値 (Returns):
        PlcClient: 接続されたPLCクライアント (Connected PLC client)
    """
    try:
        logger.info(f"Connecting with 3E frame: {host}:{port}")
        plc = PlcClient(
            host=host,
            port=port,
            timeout=2.0,
            frame_type=MCProtocol.FRAME_3E,  # 3Eフレーム (デフォルト) (3E frame (default))
            # 3Eフレームの標準的なパラメータ (Standard parameters for 3E frame)
            network_no=0,       # ネットワーク番号 (0: 自局) (Network number (0: local station))
            pc_no=0xFF,         # PC番号 (0xFF: 自局) (PC number (0xFF: local station))
            unit_io=0x03FF,     # ユニットI/O番号 (0x03FF: CPU) (Unit I/O number (0x03FF: CPU))
            unit_station=0      # ユニット局番号 (Unit station number)
        )
        logger.info("Successfully connected with 3E frame")
        return plc
    except PlcCommunicationError as e:
        logger.error(f"Failed to connect with 3E frame: {e}")
        return None


def connect_with_4e_frame(host, port):
    """
    4Eフレームを使用してPLCに接続するサンプル
    Sample of connecting to PLC using 4E frame
    
    引数 (Arguments):
        host (str): PLCのホスト名またはIPアドレス (PLC hostname or IP address)
        port (int): PLCのポート番号 (PLC port number)
        
    戻り値 (Returns):
        PlcClient: 接続されたPLCクライアント (Connected PLC client)
    """
    try:
        logger.info(f"Connecting with 4E frame: {host}:{port}")
        plc = PlcClient(
            host=host,
            port=port,
            timeout=2.0,
            frame_type=MCProtocol.FRAME_4E,  # 4Eフレーム (4E frame)
            # 4Eフレームのパラメータ (ネットワーク経由での接続用) (Parameters for 4E frame (for network connection))
            network_no=0,       # ネットワーク番号 (必要に応じて変更) (Network number (change as needed))
            pc_no=0xFF,         # PC番号 (必要に応じて変更) (PC number (change as needed))
            unit_io=0x03FF,     # ユニットI/O番号 (0x03FF: CPU) (Unit I/O number (0x03FF: CPU))
            unit_station=0      # ユニット局番号 (必要に応じて変更) (Unit station number (change as needed))
        )
        logger.info("Successfully connected with 4E frame")
        return plc
    except PlcCommunicationError as e:
        logger.error(f"Failed to connect with 4E frame: {e}")
        return None


def read_write_example(plc, frame_type):
    """
    PLCデータの読み書きサンプル
    Sample of reading and writing PLC data
    
    引数 (Arguments):
        plc (PlcClient): PLCクライアント (PLC client)
        frame_type (str): フレームタイプ ("3E"または"4E") (Frame type ("3E" or "4E"))
    """
    try:
        # データ読み取り (Read data)
        logger.info(f"Reading D100 value with {frame_type} frame")
        d_value = plc.read_device('D', 100)
        logger.info(f"{frame_type} frame: D100 value: {d_value}")
        
        # データ書き込み (Write data)
        new_value = 12345
        logger.info(f"Writing {new_value} to D100 with {frame_type} frame")
        plc.write_device('D', 100, new_value)
        
        # 書き込んだ値を確認 (Verify written value)
        logger.info(f"Verifying written value with {frame_type} frame")
        d_value = plc.read_device('D', 100)
        logger.info(f"{frame_type} frame: D100 new value: {d_value}")
        
        # 複数デバイスの読み取り (Read multiple devices)
        logger.info(f"Reading D200 to D204 values with {frame_type} frame")
        d_values = plc.read_devices('D', 200, 5)
        for i, value in enumerate(d_values):
            logger.info(f"{frame_type} frame: D{200 + i} value: {value}")
        
        # 複数デバイスの書き込み (Write to multiple devices)
        logger.info(f"Writing values to D200-D204 with {frame_type} frame")
        plc.write_devices('D', 200, [1, 2, 3, 4, 5])
        
        # 書き込んだ値を確認 (Verify written values)
        logger.info(f"Verifying written values with {frame_type} frame")
        d_values = plc.read_devices('D', 200, 5)
        for i, value in enumerate(d_values):
            logger.info(f"{frame_type} frame: D{200 + i} new value: {value}")
        
    except PlcError as e:
        logger.error(f"Error occurred during {frame_type} frame communication: {e}")


def main():
    """
    メイン関数
    Main function
    """
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <PLC_IP> <PLC_PORT>")
        print("Example: python frame_type_example.py 192.168.10.10 5000")
        return
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    # パラメータの表示 (Display parameters)
    logger.info("--------------------------------------")
    logger.info("MC Protocol Communication Frame Type Comparison Sample")
    logger.info("--------------------------------------")
    logger.info(f"Target PLC: {host}:{port}")
    logger.info("--------------------------------------")
    
    # 3Eフレームでの通信例 (Communication example with 3E frame)
    plc_3e = None
    try:
        plc_3e = connect_with_3e_frame(host, port)
        if plc_3e:
            read_write_example(plc_3e, "3E")
    finally:
        if plc_3e:
            logger.info("Closing 3E frame connection")
            plc_3e.close()
    
    logger.info("--------------------------------------")
    
    # 4Eフレームでの通信例 (Communication example with 4E frame)
    plc_4e = None
    try:
        plc_4e = connect_with_4e_frame(host, port)
        if plc_4e:
            read_write_example(plc_4e, "4E")
    finally:
        if plc_4e:
            logger.info("Closing 4E frame connection")
            plc_4e.close()
    
    logger.info("--------------------------------------")
    logger.info("Sample execution completed")


if __name__ == "__main__":
    main() 