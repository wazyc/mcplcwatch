"""
error.py - PLCとの通信中に発生する可能性のあるエラーを定義するモジュール
error.py - Module defining errors that may occur during communication with PLCs

本モジュールには、mcplcwatchライブラリで使用されるエラークラスが含まれています。
これらのエラーは、PLCとの通信中に発生する様々な問題を適切に処理するために使用されます。

This module contains error classes used by the mcplcwatch library.
These errors are used to properly handle various issues that may occur during communication with PLCs.
"""


class PlcError(Exception):
    """
    PLCとの通信中に発生するエラーの基底クラス
    Base class for errors that occur during communication with PLCs
    
    このクラスは、PLCとの通信中に発生する可能性のあるすべてのエラーの基底クラスです。
    より具体的なエラータイプは、このクラスを継承します。
    
    This class is the base class for all errors that may occur during communication with PLCs.
    More specific error types inherit from this class.
    
    属性 (Attributes):
        message (str): エラーメッセージ (Error message)
    """
    
    def __init__(self, message="An error occurred during communication with the PLC"):
        """
        初期化メソッド
        Initialization method
        
        引数 (Arguments):
            message (str): エラーメッセージ (Error message)
        """
        self.message = message
        super().__init__(self.message)


class PlcCommunicationError(PlcError):
    """
    PLCとの通信中に発生するネットワーク関連のエラークラス
    Network-related error class that occurs during communication with PLCs
    
    このクラスは、ネットワーク接続の問題やソケットエラーなど、
    通信関連の問題が発生した場合に使用されます。
    
    This class is used when communication-related problems occur,
    such as network connection issues or socket errors.
    
    属性 (Attributes):
        message (str): エラーメッセージ (Error message)
        cause: 根本的な例外 (Root cause exception)
    """
    
    def __init__(self, message="Network error occurred during communication with the PLC", cause=None):
        """
        初期化メソッド
        Initialization method
        
        引数 (Arguments):
            message (str): エラーメッセージ (Error message)
            cause: 根本的な例外 (Root cause exception)
        """
        self.cause = cause
        if cause:
            message = f"{message}: {str(cause)}"
        super().__init__(message)


class PlcDeviceError(PlcError):
    """
    PLCのデバイスに関連するエラークラス
    Error class related to PLC devices
    
    このクラスは、存在しないデバイスへのアクセスや無効なデバイスタイプの指定など、
    PLCのデバイスに関連する問題が発生した場合に使用されます。
    
    This class is used when problems related to PLC devices occur,
    such as accessing non-existent devices or specifying invalid device types.
    
    属性 (Attributes):
        message (str): エラーメッセージ (Error message)
        device_type (str): エラーが発生したデバイスのタイプ (Type of device where the error occurred)
        device_number (int): エラーが発生したデバイスの番号 (Number of device where the error occurred)
    """
    
    def __init__(self, message="An error related to PLC device occurred", device_type=None, device_number=None):
        """
        初期化メソッド
        Initialization method
        
        引数 (Arguments):
            message (str): エラーメッセージ (Error message)
            device_type (str): エラーが発生したデバイスのタイプ (Type of device where the error occurred)
            device_number (int): エラーが発生したデバイスの番号 (Number of device where the error occurred)
        """
        self.device_type = device_type
        self.device_number = device_number
        
        if device_type and device_number is not None:
            message = f"{message}: {device_type}{device_number}"
        elif device_type:
            message = f"{message}: Device type {device_type}"
        elif device_number is not None:
            message = f"{message}: Device number {device_number}"
            
        super().__init__(message)


class PlcTimeoutError(PlcError):
    """
    PLCとの通信中にタイムアウトが発生した場合のエラークラス
    Error class for timeouts that occur during communication with PLCs
    
    このクラスは、PLCからの応答がタイムアウト時間内に受信されなかった場合に使用されます。
    
    This class is used when a response from the PLC is not received within the timeout period.
    
    属性 (Attributes):
        message (str): エラーメッセージ (Error message)
        timeout (float): タイムアウト時間（秒） (Timeout period in seconds)
    """
    
    def __init__(self, message="Timeout occurred during communication with the PLC", timeout=None):
        """
        初期化メソッド
        Initialization method
        
        引数 (Arguments):
            message (str): エラーメッセージ (Error message)
            timeout (float): タイムアウト時間（秒） (Timeout period in seconds)
        """
        self.timeout = timeout
        
        if timeout is not None:
            message = f"{message}: Timeout period {timeout} seconds"
            
        super().__init__(message) 