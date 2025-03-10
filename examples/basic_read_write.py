"""
basic_read_write.py - mcplcwatchライブラリの基本的な読み書き機能を示すサンプルスクリプト
basic_read_write.py - Sample script demonstrating basic read and write functionality of the mcplcwatch library

本スクリプトは、mcplcwatchライブラリを使用して、PLCのデバイスデータを読み書きする基本的な方法を示しています。
This script demonstrates basic methods for reading and writing PLC device data using the mcplcwatch library.
"""

import sys
import time
import logging
from mcplcwatch import PlcClient, PlcError, PlcCommunicationError, PlcTimeoutError, PlcDeviceError

# ロギングの設定 (Logging configuration)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_data_example(plc):
    """
    データ読み取りのサンプル
    Sample of data reading
    
    引数 (Arguments):
        plc (PlcClient): PLCクライアントインスタンス (PLC client instance)
    """
    try:
        # 単一デバイスの読み取り (Read a single device)
        d_value = plc.read_device('D', 100)
        logger.info(f"D100 value: {d_value}")
        
        # 複数デバイスの読み取り (Read multiple devices)
        d_values = plc.read_devices('D', 200, 10)  # D200からD209まで10点読み取り (Read 10 points from D200 to D209)
        for i, value in enumerate(d_values):
            logger.info(f"D{200 + i} value: {value}")
        
        # ビットデバイスの読み取り (Read bit devices)
        m_value = plc.read_bits('M', 100, 8)  # M100からM107まで8点読み取り (Read 8 points from M100 to M107)
        for i, value in enumerate(m_value):
            logger.info(f"M{100 + i} value: {value}")
        
        # 文字列の読み取り (Read string)
        str_value = plc.read_string('D', 300, max_length=20)
        logger.info(f"String from D300: {str_value}")
        
    except PlcCommunicationError as e:
        logger.error(f"Communication error: {e}")
    except PlcTimeoutError as e:
        logger.error(f"Timeout error: {e}")
    except PlcDeviceError as e:
        logger.error(f"Device error: {e}")
    except PlcError as e:
        logger.error(f"PLC error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def write_data_example(plc):
    """
    データ書き込みのサンプル
    Sample of data writing
    
    引数 (Arguments):
        plc (PlcClient): PLCクライアントインスタンス (PLC client instance)
    """
    try:
        # 単一デバイスの書き込み (Write to a single device)
        plc.write_device('D', 100, 12345)
        logger.info("Wrote 12345 to D100")
        
        # 複数デバイスの書き込み (Write to multiple devices)
        plc.write_devices('D', 200, [1, 2, 3, 4, 5])  # D200からD204に連続して値を書き込み (Write values sequentially to D200-D204)
        logger.info("Wrote [1, 2, 3, 4, 5] to D200-D204")
        
        # ビットデバイスの書き込み (Write to bit devices)
        plc.write_bits('M', 100, [True, False, True, False, True])  # M100からM104に連続して値を書き込み (Write values sequentially to M100-M104)
        logger.info("Wrote [True, False, True, False, True] to M100-M104")
        
        # 文字列の書き込み (Write string)
        plc.write_string('D', 300, "Hello PLC!")
        logger.info("Wrote 'Hello PLC!' to D300")
        
    except PlcCommunicationError as e:
        logger.error(f"Communication error: {e}")
    except PlcTimeoutError as e:
        logger.error(f"Timeout error: {e}")
    except PlcDeviceError as e:
        logger.error(f"Device error: {e}")
    except PlcError as e:
        logger.error(f"PLC error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def main():
    """
    メイン関数
    Main function
    """
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <PLC_IP> <PLC_PORT>")
        print("Example: python basic_read_write.py 192.168.10.10 5000")
        return
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    try:
        # PLCに接続 (Connect to PLC)
        logger.info(f"Connecting to PLC: {host}:{port}")
        plc = PlcClient(host=host, port=port, timeout=2.0)
        
        # 読み取りサンプルの実行 (Run read sample)
        logger.info("Running read example...")
        read_data_example(plc)
        
        time.sleep(1)
        
        # 書き込みサンプルの実行 (Run write sample)
        logger.info("Running write example...")
        write_data_example(plc)
        
        time.sleep(1)
        
        # 書き込んだ値を読み取る (Read the written values)
        logger.info("Verifying written values...")
        read_data_example(plc)
        
    except PlcCommunicationError as e:
        logger.error(f"Communication error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # 接続を閉じる (Close connection)
        logger.info("Closing connection to PLC")
        if 'plc' in locals():
            plc.close()


if __name__ == "__main__":
    main() 