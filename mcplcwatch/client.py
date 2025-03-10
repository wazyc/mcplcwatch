"""
client.py - PLCとの通信を行うクライアントモジュール
client.py - Client module for communicating with PLCs

本モジュールには、MCプロトコルを使用してPLCとの通信を行うためのクライアントクラスが含まれています。
基本的な読み書き機能を提供します。

This module contains a client class for communicating with PLCs using the MC protocol.
It provides basic read and write functionality.
"""

import socket
import time
from .protocol import MCProtocol
from .error import PlcError, PlcCommunicationError, PlcDeviceError, PlcTimeoutError


class PlcClient:
    """
    PLCとの通信を行うクライアントクラス
    Client class for communicating with PLCs
    
    このクラスは、MCプロトコルを使用してPLCとの通信を行うための基本的な機能を提供します。
    デバイスの読み書きや文字列の読み書きなどの操作が可能です。
    
    This class provides basic functionality for communicating with PLCs using the MC protocol.
    It supports operations such as reading and writing devices and strings.
    
    属性 (Attributes):
        host (str): PLCのホスト名またはIPアドレス (PLC hostname or IP address)
        port (int): PLCのポート番号 (PLC port number)
        timeout (float): 通信タイムアウト時間（秒） (Communication timeout in seconds)
        sock (socket): 通信用ソケット (Socket for communication)
        frame_type (str): 使用するフレームタイプ ("3E"または"4E") (Frame type to use ("3E" or "4E"))
        network_no (int): ネットワーク番号 (Network number)
        pc_no (int): PC番号 (PC number)
        unit_io (int): ユニットI/O番号 (Unit I/O number)
        unit_station (int): ユニット局番号 (Unit station number)
    """
    
    def __init__(self, host, port, timeout=1.0, auto_reconnect=True, frame_type=MCProtocol.FRAME_3E,
                 network_no=0, pc_no=0xFF, unit_io=0x03FF, unit_station=0):
        """
        初期化メソッド
        Initialization method
        
        引数 (Arguments):
            host (str): PLCのホスト名またはIPアドレス (PLC hostname or IP address)
            port (int): PLCのポート番号 (PLC port number)
            timeout (float): 通信タイムアウト時間（秒） (Communication timeout in seconds)
            auto_reconnect (bool): 通信エラー時に自動的に再接続するかどうか (Whether to automatically reconnect on communication errors)
            frame_type (str): 使用するフレームタイプ ("3E"または"4E") (Frame type to use ("3E" or "4E"))
            network_no (int): ネットワーク番号 (Network number)
            pc_no (int): PC番号 (PC number)
            unit_io (int): ユニットI/O番号 (Unit I/O number)
            unit_station (int): ユニット局番号 (Unit station number)
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect
        self.buffer_size = 1024
        self.sock = None
        self.connected = False
        
        # MCプロトコル設定 (MC protocol settings)
        if frame_type not in [MCProtocol.FRAME_3E, MCProtocol.FRAME_4E]:
            raise ValueError(f"Unsupported frame type: {frame_type}")
        self.frame_type = frame_type
        self.network_no = network_no
        self.pc_no = pc_no
        self.unit_io = unit_io
        self.unit_station = unit_station
        
        # 接続 (Connection)
        self.connect()
    
    def __del__(self):
        """
        デストラクタ
        Destructor
        
        オブジェクトが破棄される際にソケットを閉じます。
        Closes the socket when the object is destroyed.
        """
        self.close()
    
    def connect(self):
        """
        PLCに接続する
        Connect to the PLC
        
        戻り値 (Returns):
            bool: 接続に成功した場合はTrue、失敗した場合はFalse (True if connection was successful, False otherwise)
        
        例外 (Exceptions):
            PlcCommunicationError: 接続に失敗した場合 (When connection fails)
        """
        try:
            # 既存の接続を閉じる (Close existing connection)
            if self.sock:
                self.close()
            
            # 新しい接続を作成 (Create new connection)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            self.connected = True
            return True
        except socket.error as e:
            self.connected = False
            raise PlcCommunicationError(f"Failed to connect to PLC: {self.host}:{self.port}", e)
    
    def close(self):
        """
        接続を閉じる
        Close the connection
        """
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.connected = False
    
    def _send_and_receive(self, frame):
        """
        フレームを送信し、応答を受信する
        Send a frame and receive the response
        
        引数 (Arguments):
            frame (bytes): 送信するフレーム (Frame to send)
            
        戻り値 (Returns):
            bytes: 受信した応答 (Received response)
            
        例外 (Exceptions):
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        # 接続されていない場合は接続 (Connect if not connected)
        if not self.connected:
            self.connect()
        
        try:
            # フレーム送信 (Send frame)
            self.sock.sendall(frame)
            
            # 応答受信 (Receive response)
            response = self.sock.recv(1024)
            
            # 応答のチェック (エラーコードなど) (Check response for error codes, etc.)
            min_response_length = 11 if self.frame_type == '3E' else 15
            if len(response) < min_response_length:  # 最小応答長 (Minimum response length)
                raise PlcCommunicationError(f"Response too short: {len(response)} bytes")
            
            # エンドコード (正常終了: 0, エラー: 非0) - フレームタイプによってオフセットが異なる
            # End code (Normal completion: 0, Error: non-zero) - offset differs by frame type
            if self.frame_type == '3E':
                end_code_offset = 9
            else:  # FRAME_4E
                end_code_offset = 11
            end_code = int.from_bytes(response[end_code_offset:end_code_offset+2], byteorder='little')
            
            if end_code != 0:
                # 代表的なエラーコードのメッセージ (Typical error code messages)
                error_messages = {
                    0xC050: "Read/write request to unsupported device",
                    0xC051: "Read/write request with unsupported number of points",
                    0xC052: "Read/write request to word device with bit specification",
                    0xC054: "Read/write request with invalid specification of device",
                    0xC056: "Read/write request with device out of range",
                    0xC059: "Read/write request with invalid specification of data count",
                    0xC05B: "Read/write request with invalid specification of stored data",
                    0xC05C: "Read/write request with invalid specification of block",
                    0xC06B: "Request when CPU is in RUN mode and writing is disabled"
                }
                error_msg = error_messages.get(end_code, f"Unknown error code: 0x{end_code:04X}")
                raise PlcCommunicationError(f"PLC returned error: {error_msg} (0x{end_code:04X})")
            
            return response
            
        except socket.timeout:
            # タイムアウト時は接続状態をリセット (Reset connection status on timeout)
            self.connected = False
            raise PlcTimeoutError(f"Timeout occurred while communicating with PLC")
            
        except socket.error as e:
            # その他のソケットエラー時も接続状態をリセット (Reset connection status on other socket errors)
            self.connected = False
            raise PlcCommunicationError(f"Socket error occurred: {e}")
    
    def is_bit_device(self, device_type):
        """
        指定されたデバイスタイプがビットデバイスかどうかを判定する
        Determine if the specified device type is a bit device
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Device type)
            
        戻り値 (Returns):
            bool: ビットデバイスの場合はTrue、ワードデバイスの場合はFalse (True if it's a bit device, False if it's a word device)
        """
        return device_type in MCProtocol.BIT_DEVICES
    
    def read_devices(self, device_type, device_number, count=1):
        """
        デバイスを読み出す
        Read devices
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (D, M, X, Yなど) (Device type (D, M, X, Y, etc.))
            device_number (int): 先頭デバイス番号 (Starting device number)
            count (int): 読み出すデバイス点数 (Number of device points to read)
            
        戻り値 (Returns):
            list: 読み出したデータのリスト (List of read data)
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        # デバイスタイプのチェック (Check device type)
        if device_type not in MCProtocol.DEVICE_CODES:
            raise PlcDeviceError(f"Unsupported device type", device_type)
        
        # ビットデバイスかどうかの判定 (Determine if it's a bit device)
        is_bit = self.is_bit_device(device_type)
        
        # 読み出しフレームの作成 (Create read frame)
        frame = MCProtocol.create_read_frame(
            device_type, device_number, count, is_bit,
            frame_type=self.frame_type,
            network_no=self.network_no,
            pc_no=self.pc_no,
            unit_io=self.unit_io,
            unit_station=self.unit_station
        )
        
        # 送信と受信 (Send and receive)
        response = self._send_and_receive(frame)
        
        # 応答の解析 (Parse response)
        return MCProtocol.parse_read_response(response, count, is_bit, self.frame_type)
    
    def read_device(self, device_type, device_number):
        """
        単一デバイスを読み出す
        Read a single device
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (D, M, X, Yなど) (Device type (D, M, X, Y, etc.))
            device_number (int): デバイス番号 (Device number)
            
        戻り値 (Returns):
            int or bool: 読み出したデータ (ビットデバイスの場合はブール値、ワードデバイスの場合は整数値) (Read data (boolean for bit devices, integer for word devices))
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        result = self.read_devices(device_type, device_number, 1)
        return result[0]
    
    def write_devices(self, device_type, device_number, values):
        """
        デバイスに値を書き込む
        Write values to devices
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (D, M, X, Yなど) (Device type (D, M, X, Y, etc.))
            device_number (int): 先頭デバイス番号 (Starting device number)
            values (list): 書き込む値のリスト (List of values to write)
            
        戻り値 (Returns):
            bool: 書き込みに成功した場合はTrue (True if writing was successful)
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        # デバイスタイプのチェック (Check device type)
        if device_type not in MCProtocol.DEVICE_CODES:
            raise PlcDeviceError(f"Unsupported device type", device_type)
        
        # 値が単一の場合はリストに変換 (Convert single value to list)
        if not isinstance(values, list):
            values = [values]
        
        # ビットデバイスかどうかの判定 (Determine if it's a bit device)
        is_bit = self.is_bit_device(device_type)
        
        # ビットデバイスの場合は、値をブール値に変換 (Convert values to boolean for bit devices)
        if is_bit:
            values = [bool(v) for v in values]
        
        # 書き込みフレームの作成 (Create write frame)
        frame = MCProtocol.create_write_frame(
            device_type, device_number, values, is_bit,
            frame_type=self.frame_type,
            network_no=self.network_no,
            pc_no=self.pc_no,
            unit_io=self.unit_io,
            unit_station=self.unit_station
        )
        
        # 送信と受信 (Send and receive)
        response = self._send_and_receive(frame)
        
        # 応答のチェック (エラーコードなど) (Check response for error codes, etc.)
        return True
    
    def write_device(self, device_type, device_number, value):
        """
        単一デバイスに値を書き込む
        Write a value to a single device
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (D, M, X, Yなど) (Device type (D, M, X, Y, etc.))
            device_number (int): デバイス番号 (Device number)
            value (int or bool): 書き込む値 (Value to write)
            
        戻り値 (Returns):
            bool: 書き込みに成功した場合はTrue (True if writing was successful)
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        return self.write_devices(device_type, device_number, [value])
    
    def read_string(self, device_type, device_number, max_length=80):
        """
        文字列を読み出す
        Read a string
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Dなど、ワードデバイスのみ) (Device type (D, etc., word devices only))
            device_number (int): 先頭デバイス番号 (Starting device number)
            max_length (int): 読み出す最大文字数 (バイト数ではなく、文字数) (Maximum number of characters to read (characters, not bytes))
            
        戻り値 (Returns):
            str: 読み出した文字列 (Read string)
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        # デバイスタイプのチェック (ワードデバイスのみ) (Check device type (word devices only))
        if device_type not in MCProtocol.WORD_DEVICES:
            raise PlcDeviceError(f"String reading is only supported for word devices", device_type)
        
        # 必要なワード数の計算 (1ワード = 2バイト) (Calculate required word count (1 word = 2 bytes))
        # UTF-8では1文字最大3バイトなので、最大長さ*3/2でワード数を計算 (In UTF-8, 1 character is max 3 bytes, so calculate word count as max_length*3/2)
        word_count = (max_length * 3 + 1) // 2
        
        # データの読み出し (Read data)
        data = self.read_devices(device_type, device_number, word_count)
        
        # ワードデータから文字列を解析 (Parse string from word data)
        return MCProtocol.parse_string_data(data)
    
    def write_string(self, device_type, device_number, string_value):
        """
        文字列を書き込む
        Write a string
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (Dなど、ワードデバイスのみ) (Device type (D, etc., word devices only))
            device_number (int): 先頭デバイス番号 (Starting device number)
            string_value (str): 書き込む文字列 (String to write)
            
        戻り値 (Returns):
            bool: 書き込みに成功した場合はTrue (True if writing was successful)
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        # デバイスタイプのチェック (ワードデバイスのみ) (Check device type (word devices only))
        if device_type not in MCProtocol.WORD_DEVICES:
            raise PlcDeviceError(f"String writing is only supported for word devices", device_type)
        
        # 文字列書き込みフレームの作成 (Create string write frame)
        frame = MCProtocol.create_write_string_frame(
            device_type, device_number, string_value,
            frame_type=self.frame_type,
            network_no=self.network_no,
            pc_no=self.pc_no,
            unit_io=self.unit_io,
            unit_station=self.unit_station
        )
        
        # 送信と受信 (Send and receive)
        response = self._send_and_receive(frame)
        
        # 応答のチェック (エラーコードなど) (Check response for error codes, etc.)
        return True
    
    def read_bits(self, device_type, device_number, count=1):
        """
        ビットデバイスを読み出す (read_devicesのエイリアス)
        Read bit devices (alias of read_devices)
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (M, X, Yなど) (Device type (M, X, Y, etc.))
            device_number (int): 先頭デバイス番号 (Starting device number)
            count (int): 読み出すデバイス点数 (Number of device points to read)
            
        戻り値 (Returns):
            list: 読み出したデータのリスト (ブール値) (List of read data (boolean values))
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        if device_type not in MCProtocol.BIT_DEVICES:
            raise PlcDeviceError(f"Only bit devices can be read with read_bits method", device_type)
        
        return self.read_devices(device_type, device_number, count)
    
    def read_words(self, device_type, device_number, count=1):
        """
        ワードデバイスを読み出す (read_devicesのエイリアス)
        Read word devices (alias of read_devices)
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (D, Wなど) (Device type (D, W, etc.))
            device_number (int): 先頭デバイス番号 (Starting device number)
            count (int): 読み出すデバイス点数 (Number of device points to read)
            
        戻り値 (Returns):
            list: 読み出したデータのリスト (整数値) (List of read data (integer values))
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        if device_type not in MCProtocol.WORD_DEVICES:
            raise PlcDeviceError(f"Only word devices can be read with read_words method", device_type)
        
        return self.read_devices(device_type, device_number, count)
    
    def write_bits(self, device_type, device_number, values):
        """
        ビットデバイスに値を書き込む (write_devicesのエイリアス)
        Write values to bit devices (alias of write_devices)
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (M, X, Yなど) (Device type (M, X, Y, etc.))
            device_number (int): 先頭デバイス番号 (Starting device number)
            values (list): 書き込む値のリスト (ブール値) (List of values to write (boolean values))
            
        戻り値 (Returns):
            bool: 書き込みに成功した場合はTrue (True if writing was successful)
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        if device_type not in MCProtocol.BIT_DEVICES:
            raise PlcDeviceError(f"Only bit devices can be written with write_bits method", device_type)
        
        return self.write_devices(device_type, device_number, values)
    
    def write_words(self, device_type, device_number, values):
        """
        ワードデバイスに値を書き込む (write_devicesのエイリアス)
        Write values to word devices (alias of write_devices)
        
        引数 (Arguments):
            device_type (str): デバイスタイプ (D, Wなど) (Device type (D, W, etc.))
            device_number (int): 先頭デバイス番号 (Starting device number)
            values (list): 書き込む値のリスト (整数値) (List of values to write (integer values))
            
        戻り値 (Returns):
            bool: 書き込みに成功した場合はTrue (True if writing was successful)
            
        例外 (Exceptions):
            PlcDeviceError: デバイスタイプが不正な場合 (When the device type is invalid)
            PlcCommunicationError: 通信中にエラーが発生した場合 (When an error occurs during communication)
            PlcTimeoutError: タイムアウトが発生した場合 (When a timeout occurs)
        """
        if device_type not in MCProtocol.WORD_DEVICES:
            raise PlcDeviceError(f"Only word devices can be written with write_words method", device_type)
        
        return self.write_devices(device_type, device_number, values) 