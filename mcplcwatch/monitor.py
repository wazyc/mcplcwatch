"""
monitor.py - PLCのデータ監視を行うモジュール
monitor.py - Module for monitoring PLC data

本モジュールには、PLCのデータを周期的に監視し、変化を検出するためのクラスが含まれています。
変化を検出した場合には、指定されたコールバック関数を呼び出します。

This module contains classes for periodically monitoring PLC data and detecting changes.
When changes are detected, it calls the specified callback functions.
"""

import threading
import time
import logging
from .client import PlcClient
from .error import PlcError, PlcCommunicationError, PlcTimeoutError


# ロガーの設定 (Logger configuration)
logger = logging.getLogger(__name__)


class DeviceMonitor:
    """
    単一デバイスの監視を行うクラス
    Class for monitoring a single device
    
    このクラスは、単一のデバイスを監視し、値が変化した場合にコールバック関数を呼び出します。
    
    This class monitors a single device and calls a callback function when the value changes.
    
    属性 (Attributes):
        device_type (str): デバイスタイプ (Device type)
        device_number (int): デバイス番号 (Device number)
        last_value: 最後に読み取った値 (Last read value)
        callback: 値が変化した場合に呼び出されるコールバック関数 (Callback function called when the value changes)
        on_error: エラーが発生した場合に呼び出されるコールバック関数 (Callback function called when an error occurs)
    """
    
    def __init__(self, device_type, device_number, callback=None, on_error=None):
        """
        初期化メソッド
        Initialization method
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Device type)
            device_number (int): デバイス番号 (Device number)
            callback: 値が変化した場合に呼び出されるコールバック関数 (Callback function called when the value changes)
            on_error: エラーが発生した場合に呼び出されるコールバック関数 (Callback function called when an error occurs)
        """
        self.device_type = device_type
        self.device_number = device_number
        self.last_value = None
        self.callback = callback
        self.on_error = on_error
    
    def update(self, value):
        """
        デバイスの値を更新し、変化があった場合にコールバック関数を呼び出す
        Update the device value and call the callback function if there is a change
        
        引数 (Arguments):
            value: デバイスの新しい値 (New value of the device)
            
        戻り値 (Returns):
            bool: 値が変化した場合はTrue、変化がない場合はFalse (True if the value changed, False otherwise)
        """
        if self.last_value != value:
            old_value = self.last_value
            self.last_value = value
            
            if self.callback and old_value is not None:
                try:
                    self.callback(self.device_type, self.device_number, old_value, value)
                except Exception as e:
                    logger.error(f"Error occurred in callback function: {e}")
            
            return True
        return False
    
    def handle_error(self, error):
        """
        エラーを処理する
        Handle an error
        
        引数 (Arguments):
            error: 発生したエラー (Error that occurred)
        """
        if self.on_error:
            try:
                self.on_error(self.device_type, self.device_number, error)
            except Exception as e:
                logger.error(f"Error occurred in error callback function: {e}")


class DeviceGroupMonitor:
    """
    複数の連続したデバイスの監視を行うクラス
    Class for monitoring multiple consecutive devices
    
    このクラスは、連続した複数のデバイスを一括で監視し、値が変化した場合にコールバック関数を呼び出します。
    
    This class monitors multiple consecutive devices in bulk and calls a callback function when the values change.
    
    属性 (Attributes):
        device_type (str): デバイスタイプ (Device type)
        start_number (int): 開始デバイス番号 (Starting device number)
        count (int): デバイス数 (Number of devices)
        last_values (list): 最後に読み取った値のリスト (List of last read values)
        callback: 値が変化した場合に呼び出されるコールバック関数 (Callback function called when the values change)
        on_error: エラーが発生した場合に呼び出されるコールバック関数 (Callback function called when an error occurs)
    """
    
    def __init__(self, device_type, start_number, count, callback=None, on_error=None):
        """
        初期化メソッド
        Initialization method
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Device type)
            start_number (int): 開始デバイス番号 (Starting device number)
            count (int): デバイス数 (Number of devices)
            callback: 値が変化した場合に呼び出されるコールバック関数 (Callback function called when the values change)
            on_error: エラーが発生した場合に呼び出されるコールバック関数 (Callback function called when an error occurs)
        """
        self.device_type = device_type
        self.start_number = start_number
        self.count = count
        self.last_values = None
        self.callback = callback
        self.on_error = on_error
    
    def update(self, values):
        """
        デバイスグループの値を更新し、変化があった場合にコールバック関数を呼び出す
        Update the device group values and call the callback function if there are changes
        
        引数 (Arguments):
            values: デバイスの新しい値のリスト (List of new device values)
            
        戻り値 (Returns):
            bool: 値が変化した場合はTrue、変化がない場合はFalse (True if any value changed, False otherwise)
        """
        if self.last_values != values:
            if self.last_values is None:
                self.last_values = values.copy()
                return True
            
            # 変化を検出 (Detect changes)
            changed = False
            for i, (old_value, new_value) in enumerate(zip(self.last_values, values)):
                if old_value != new_value:
                    device_number = self.start_number + i
                    
                    if self.callback:
                        try:
                            self.callback(self.device_type, device_number, old_value, new_value)
                        except Exception as e:
                            logger.error(f"Error occurred in callback function: {e}")
                    
                    changed = True
            
            # 最新の値を保存 (Save the latest values)
            self.last_values = values.copy()
            return changed
        
        return False
    
    def handle_error(self, error):
        """
        エラーを処理する
        Handle an error
        
        引数 (Arguments):
            error: 発生したエラー (Error that occurred)
        """
        if self.on_error:
            try:
                self.on_error(self.device_type, f"{self.start_number}-{self.start_number + self.count - 1}", error)
            except Exception as e:
                logger.error(f"Error occurred in error callback function: {e}")


class PlcMonitor:
    """
    PLCのデータを監視するクラス
    Class for monitoring PLC data
    
    このクラスは、複数のデバイスを周期的に監視し、値が変化した場合にコールバック関数を呼び出します。
    
    This class periodically monitors multiple devices and calls callback functions when values change.
    
    属性 (Attributes):
        plc (PlcClient): PLCクライアント (PLC client)
        monitors (list): 監視対象のデバイスモニターのリスト (List of device monitors to monitor)
        group_monitors (list): 監視対象のデバイスグループモニターのリスト (List of device group monitors to monitor)
        interval (float): 監視周期（秒） (Monitoring interval in seconds)
        running (bool): 監視中かどうか (Whether monitoring is running)
        thread: 監視スレッド (Monitoring thread)
    """
    
    def __init__(self, plc_client, interval=1.0, auto_start=False):
        """
        初期化メソッド
        Initialization method
        
        引数 (Arguments):
            plc_client (PlcClient): PLCクライアント (PLC client)
            interval (float): 監視周期（秒） (Monitoring interval in seconds)
            auto_start (bool): 監視を自動的に開始するかどうか (Whether to automatically start monitoring)
        """
        self.plc = plc_client
        self.monitors = []
        self.group_monitors = []
        self.interval = interval
        self.running = False
        self.thread = None
        
        if auto_start:
            self.start()
    
    def add_device(self, device_type, device_number, callback=None, on_error=None):
        """
        監視対象のデバイスを追加する
        Add a device to monitor
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Device type)
            device_number (int): デバイス番号 (Device number)
            callback: 値が変化した場合に呼び出されるコールバック関数 (Callback function called when the value changes)
            on_error: エラーが発生した場合に呼び出されるコールバック関数 (Callback function called when an error occurs)
            
        戻り値 (Returns):
            DeviceMonitor: 追加されたデバイスモニター (Added device monitor)
        """
        monitor = DeviceMonitor(device_type, device_number, callback, on_error)
        self.monitors.append(monitor)
        
        # 初期値を読み込む (Read initial value)
        try:
            value = self.plc.read_device(device_type, device_number)
            monitor.last_value = value
        except PlcError as e:
            logger.warning(f"Failed to read initial value: {e} (初期値の読み込みに失敗しました)")
            if on_error:
                monitor.handle_error(e)
        
        return monitor
    
    def add_devices(self, device_type, start_number, count, callback=None, on_error=None):
        """
        監視対象のデバイスグループを追加する
        Add a group of devices to monitor
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Device type)
            start_number (int): 開始デバイス番号 (Starting device number)
            count (int): デバイス数 (Number of devices)
            callback: 値が変化した場合に呼び出されるコールバック関数 (Callback function called when the values change)
            on_error: エラーが発生した場合に呼び出されるコールバック関数 (Callback function called when an error occurs)
            
        戻り値 (Returns):
            DeviceGroupMonitor: 追加されたデバイスグループモニター (Added device group monitor)
        """
        monitor = DeviceGroupMonitor(device_type, start_number, count, callback, on_error)
        self.group_monitors.append(monitor)
        
        # 初期値を読み込む (Read initial values)
        try:
            values = self.plc.read_devices(device_type, start_number, count)
            monitor.last_values = values.copy()
        except PlcError as e:
            logger.warning(f"Failed to read initial values: {e} (初期値の読み込みに失敗しました)")
            if on_error:
                monitor.handle_error(e)
        
        return monitor
    
    def remove_device(self, device_type, device_number):
        """
        監視対象のデバイスを削除する
        Remove a device from monitoring
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Device type)
            device_number (int): デバイス番号 (Device number)
            
        戻り値 (Returns):
            bool: 削除に成功した場合はTrue、失敗した場合はFalse (True if removal was successful, False otherwise)
        """
        for i, monitor in enumerate(self.monitors):
            if monitor.device_type == device_type and monitor.device_number == device_number:
                self.monitors.pop(i)
                return True
        return False
    
    def remove_devices(self, device_type, start_number, count):
        """
        監視対象のデバイスグループを削除する
        Remove a group of devices from monitoring
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Device type)
            start_number (int): 開始デバイス番号 (Starting device number)
            count (int): デバイス数 (Number of devices)
            
        戻り値 (Returns):
            bool: 削除に成功した場合はTrue、失敗した場合はFalse (True if removal was successful, False otherwise)
        """
        for i, monitor in enumerate(self.group_monitors):
            if (monitor.device_type == device_type and 
                monitor.start_number == start_number and 
                monitor.count == count):
                self.group_monitors.pop(i)
                return True
        return False
    
    def clear(self):
        """
        すべての監視対象をクリアする
        Clear all monitoring targets
        """
        self.monitors.clear()
        self.group_monitors.clear()
    
    def start(self, interval=None):
        """
        監視を開始する
        Start monitoring
        
        引数 (Arguments):
            interval (float): 監視周期（秒） (Monitoring interval in seconds)
        """
        if interval is not None:
            self.interval = interval
        
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        """
        監視を停止する
        Stop monitoring
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=self.interval * 2)
            self.thread = None
    
    def _monitor_loop(self):
        """
        監視ループの内部メソッド
        Internal method for the monitoring loop
        """
        while self.running:
            start_time = time.time()
            
            # 単一デバイスの監視 (Monitor single devices)
            for monitor in self.monitors:
                try:
                    value = self.plc.read_device(monitor.device_type, monitor.device_number)
                    monitor.update(value)
                except PlcError as e:
                    logger.error(f"Failed to read device: {monitor.device_type}{monitor.device_number}: {e}")
                    monitor.handle_error(e)
                except Exception as e:
                    logger.error(f"Unexpected error occurred: {e}")
            
            # デバイスグループの監視 (Monitor device groups)
            for monitor in self.group_monitors:
                try:
                    values = self.plc.read_devices(monitor.device_type, monitor.start_number, monitor.count)
                    monitor.update(values)
                except PlcError as e:
                    logger.error(f"Failed to read device group: {monitor.device_type}{monitor.start_number}-{monitor.start_number + monitor.count - 1}: {e}")
                    monitor.handle_error(e)
                except Exception as e:
                    logger.error(f"Unexpected error occurred: {e}")
            
            # 次の周期まで待機 (Wait until the next cycle)
            elapsed = time.time() - start_time
            if elapsed < self.interval:
                time.sleep(self.interval - elapsed)
            else:
                logger.warning(f"Monitoring cycle took too long: {elapsed:.3f} seconds (監視周期が間に合いませんでした)")
    
    def is_running(self):
        """
        監視が実行中かどうかを返す
        Returns whether monitoring is running
        
        戻り値 (Returns):
            bool: 監視が実行中の場合はTrue、そうでない場合はFalse (True if monitoring is running, False otherwise)
        """
        return self.running 