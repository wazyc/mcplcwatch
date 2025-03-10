"""
mcplcwatch - MCプロトコルを使用してPLCのデータを読み書き、監視するライブラリ
mcplcwatch - A library for reading, writing, and monitoring PLC data using MC protocol

本モジュールは、三菱電機製PLCとMCプロトコルを使用して通信するためのPythonライブラリです。
データの読み書きだけでなく、指定されたデバイスの変化を監視する機能も提供します。
3Eフレームと4Eフレームをサポートしています。

This module is a Python library for communicating with Mitsubishi Electric PLCs using the MC protocol.
It provides not only data reading and writing capabilities but also functions to monitor changes in specified devices.
3E and 4E frames are supported.

主な機能 (Main features):
    - PLCデバイスからのデータ読み取り (Reading data from PLC devices)
    - PLCデバイスへのデータ書き込み (Writing data to PLC devices)
    - 複数のデバイスタイプに対応 (Support for multiple device types)
    - データの定期的な監視と変更検出 (Periodic monitoring of data and change detection)
    - 3Eフレーム、4Eフレームの両方に対応 (Support for both 3E and 4E frames)

クラス (Classes):
    - PlcClient: PLCとの基本的な通信を管理するクラス (Class for managing basic communication with PLCs)
    - PlcMonitor: PLCのデータを監視するクラス (Class for monitoring PLC data)
    - PlcError: PLCとの通信中に発生するエラーを表すクラス (Class representing errors that occur during PLC communication)
"""

__version__ = '0.1.0'

from .client import PlcClient
from .monitor import PlcMonitor
from .error import PlcError, PlcCommunicationError, PlcDeviceError, PlcTimeoutError
from .protocol import MCProtocol

__all__ = [
    'PlcClient',
    'PlcMonitor',
    'PlcError',
    'PlcCommunicationError',
    'PlcDeviceError',
    'PlcTimeoutError',
    'MCProtocol',
] 