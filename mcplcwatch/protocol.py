"""
protocol.py - MCプロトコルの定数とユーティリティ関数を含むモジュール
protocol.py - Module containing constants and utility functions for MC protocol

本モジュールには、三菱電機のMCプロトコルに関連する定数と
プロトコルの処理に使用されるユーティリティ関数が含まれています。

This module contains constants related to Mitsubishi Electric's MC protocol
and utility functions used for protocol processing.
"""


class MCProtocol:
    """
    MCプロトコルの定数とユーティリティメソッドを提供するクラス
    Class providing constants and utility methods for MC protocol
    
    このクラスには、MCプロトコルの各種コマンドコードやデバイスコードなどの定数と、
    プロトコルフレームの生成や解析に関連するユーティリティメソッドが含まれています。
    
    This class includes various command codes and device codes for the MC protocol,
    as well as utility methods related to generating and parsing protocol frames.
    """
    
    # フレームタイプ (Frame types)
    FRAME_3E = "3E"
    FRAME_4E = "4E"
    
    # サブヘッダ (フレームタイプ別) (Sub-headers by frame type)
    SUBHEADER = {
        FRAME_3E: [0x50, 0x00],  # 3Eフレーム (3E frame)
        FRAME_4E: [0x54, 0x00],  # 4Eフレーム (4E frame)
    }
    
    # コマンドコード (Command codes)
    CMD_BATCH_READ_WORD = [0x01, 0x04]    # ワード単位の一括読出し (Batch read in word units)
    CMD_BATCH_WRITE_WORD = [0x01, 0x14]   # ワード単位の一括書き込み (Batch write in word units)
    CMD_BATCH_READ_BIT = [0x01, 0x04]     # ビット単位の一括読出し (Batch read in bit units)
    CMD_BATCH_WRITE_BIT = [0x01, 0x14]    # ビット単位の一括書き込み (Batch write in bit units)
    
    # サブコマンド (MELSEC-Q/Lシリーズ用) (Sub-commands for MELSEC-Q/L series)
    SUBCMD = [0x00, 0x00]
    
    # 監視タイマ (デフォルト: 2秒) (Monitoring timer (default: 2 seconds))
    TIMER = [0x20, 0x00]
    
    # デバイスコード (Device codes)
    DEVICE_CODES = {
        'D': 0xA8,   # データレジスタ (Data register)
        'W': 0xB4,   # リンクレジスタ (Link register)
        'M': 0x90,   # 内部リレー (Internal relay)
        'X': 0x9C,   # 入力リレー (Input relay)
        'Y': 0x9D,   # 出力リレー (Output relay)
        'B': 0xA0,   # リンクリレー (Link relay)
        'SM': 0x91,  # 特殊リレー (Special relay)
        'SD': 0xA9,  # 特殊レジスタ (Special register)
        'TS': 0xC1,  # タイマ(接点) (Timer (contact))
        'TC': 0xC0,  # タイマ(コイル) (Timer (coil))
        'TN': 0xC2,  # タイマ(現在値) (Timer (current value))
        'SS': 0xC7,  # 積算タイマ(接点) (Accumulated timer (contact))
        'SC': 0xC6,  # 積算タイマ(コイル) (Accumulated timer (coil))
        'SN': 0xC8,  # 積算タイマ(現在値) (Accumulated timer (current value))
        'CS': 0xC4,  # カウンタ(接点) (Counter (contact))
        'CC': 0xC3,  # カウンタ(コイル) (Counter (coil))
        'CN': 0xC5,  # カウンタ(現在値) (Counter (current value))
        'R': 0xAF,   # ファイルレジスタ (File register)
        'ZR': 0xB0,  # ファイルレジスタ (File register)
    }
    
    # ビットデバイスのリスト (List of bit devices)
    BIT_DEVICES = ['X', 'Y', 'M', 'B', 'SM', 'TS', 'TC', 'SS', 'SC', 'CS', 'CC']
    
    # ワードデバイスのリスト (List of word devices)
    WORD_DEVICES = ['D', 'W', 'SD', 'TN', 'SN', 'CN', 'R', 'ZR']
    
    @staticmethod
    def zero_padding(value, length):
        """
        16進数文字列を0埋めする
        Zero-pad a hexadecimal string
        
        引数 (Arguments):
            value (str): 0埋めする16進数文字列 (Hexadecimal string to be zero-padded)
            length (int): 出力する文字列の長さ (Length of the output string)
            
        戻り値 (Returns):
            str: 0埋めされた16進数文字列 (Zero-padded hexadecimal string)
        """
        if len(value) >= length:
            return value
        return ('0' * length + value)[-length:]
    
    @staticmethod
    def int_to_hex_bytes(value, length=2):
        """
        整数値を指定された長さの16進数バイトのリストに変換する
        Convert an integer value to a list of hexadecimal bytes of specified length
        
        引数 (Arguments):
            value (int): 変換する整数値 (Integer value to convert)
            length (int): 出力するバイト数 (Number of bytes to output)
            
        戻り値 (Returns):
            list: 16進数バイトのリスト（リトルエンディアン） (List of hexadecimal bytes (little-endian))
        """
        result = []
        for i in range(length):
            result.append((value >> (i * 8)) & 0xFF)
        return result
    
    @staticmethod
    def hex_bytes_to_int(bytes_list):
        """
        16進数バイトのリストを整数値に変換する
        Convert a list of hexadecimal bytes to an integer value
        
        引数 (Arguments):
            bytes_list (list): 変換する16進数バイトのリスト（リトルエンディアン） (List of hexadecimal bytes to convert (little-endian))
            
        戻り値 (Returns):
            int: 変換された整数値 (Converted integer value)
        """
        result = 0
        for i, byte in enumerate(bytes_list):
            result |= byte << (i * 8)
        return result
    
    @staticmethod
    def device_number_to_bytes(device_number):
        """
        デバイス番号を3バイトの16進数バイトのリストに変換する
        Convert a device number to a list of three hexadecimal bytes
        
        引数 (Arguments):
            device_number (int): デバイス番号 (Device number)
            
        戻り値 (Returns):
            list: 3バイトの16進数バイトのリスト（リトルエンディアン） (List of three hexadecimal bytes (little-endian))
        """
        device_number_hex = MCProtocol.zero_padding(hex(device_number)[2:], 6)
        return [
            int(device_number_hex[4:], 16),
            int(device_number_hex[2:4], 16),
            int(device_number_hex[0:2], 16)
        ]
    
    @staticmethod
    def element_to_bytes(element):
        """
        要素数を2バイトの16進数バイトのリストに変換する
        Convert an element count to a list of two hexadecimal bytes
        
        引数 (Arguments):
            element (int): 要素数 (Element count)
            
        戻り値 (Returns):
            list: 2バイトの16進数バイトのリスト（リトルエンディアン） (List of two hexadecimal bytes (little-endian))
        """
        element_hex = MCProtocol.zero_padding(hex(element)[2:], 4)
        return [
            int(element_hex[2:], 16),
            int(element_hex[0:2], 16)
        ]
    
    @staticmethod
    def create_read_frame(device_type, device_number, element, is_bit=False, frame_type=FRAME_3E, network_no=0, pc_no=0xFF, unit_io=0x03FF, unit_station=0):
        """
        読み出しフレームを作成する
        Create a read frame
        
        引数 (Arguments):
            device_type (str): デバイスタイプ ('D', 'M'など) (Device type ('D', 'M', etc.))
            device_number (int): デバイス番号 (Device number)
            element (int): 読み出す要素数 (Number of elements to read)
            is_bit (bool): ビットデバイスかどうか (Whether it's a bit device)
            frame_type (str): フレームタイプ ("3E"または"4E") (Frame type ("3E" or "4E"))
            network_no (int): ネットワーク番号 (4Eフレーム用) (Network number (for 4E frame))
            pc_no (int): PC番号 (4Eフレーム用) (PC number (for 4E frame))
            unit_io (int): ユニットI/O番号 (4Eフレーム用) (Unit I/O number (for 4E frame))
            unit_station (int): ユニット局番号 (4Eフレーム用) (Unit station number (for 4E frame))
            
        戻り値 (Returns):
            bytes: 送信用のバイナリデータ (Binary data for sending)
        """
        # デバイスタイプのチェック (Check device type)
        if device_type not in MCProtocol.DEVICE_CODES:
            raise ValueError(f"Unsupported device type: {device_type}")
        
        # フレームタイプのチェック (Check frame type)
        if frame_type not in MCProtocol.SUBHEADER:
            raise ValueError(f"Unsupported frame type: {frame_type}")
        
        # コマンドの選択 (ビットデバイスかワードデバイスか) (Select command (bit device or word device))
        command = MCProtocol.CMD_BATCH_READ_BIT if is_bit else MCProtocol.CMD_BATCH_READ_WORD
        
        # フレームの共通部分を作成 (Create common part of the frame)
        frame = [
            # サブヘッダ (フレームタイプに応じて選択) (Sub-header (selected according to frame type))
            *MCProtocol.SUBHEADER[frame_type],
        ]
        
        # アクセス経路 (フレームタイプに応じて異なる) (Access path (differs according to frame type))
        if frame_type == MCProtocol.FRAME_3E:
            frame.extend([
                network_no,  # ネットワーク番号 (Network number)
                pc_no,       # PC番号 (PC number)
                unit_io & 0xFF, (unit_io >> 8) & 0xFF,  # 要求先ユニットI/O番号 (Destination unit I/O number)
                unit_station,  # 要求先ユニット局番号 (Destination unit station number)
                0x00, 0x00,  # 要求データ長 (後で設定) (Request data length (set later))
            ])
        elif frame_type == MCProtocol.FRAME_4E:
            frame.extend([
                0x00, 0x00,  # 応答データ長 (未使用) (Response data length (unused))
                0x00, 0x00,  # 要求データ長 (後で設定) (Request data length (set later))
                network_no,  # ネットワーク番号 (Network number)
                pc_no,       # PC番号 (PC number)
                0xFF, 0xFF,  # 要求先CPU監視タイマ (Destination CPU monitoring timer)
                unit_io & 0xFF, (unit_io >> 8) & 0xFF,  # 要求先ユニットI/O番号 (Destination unit I/O number)
                unit_station,  # 要求先ユニット局番号 (Destination unit station number)
            ])
        
        # 監視タイマと要求データを追加 (Add monitoring timer and request data)
        frame.extend([
            *MCProtocol.TIMER,  # 監視タイマ (Monitoring timer)
            # 要求データ (Request data)
            *command,  # コマンド (Command)
            *MCProtocol.SUBCMD,  # サブコマンド (Sub-command)
            *MCProtocol.device_number_to_bytes(device_number),  # 先頭デバイス番号 (Starting device number)
            MCProtocol.DEVICE_CODES[device_type],  # デバイスコード (Device code)
            *MCProtocol.element_to_bytes(element),  # デバイス点数 (Number of device points)
        ])
        
        # 要求データ長の設定 (フレームタイプに応じて位置が異なる) (Set request data length (position differs according to frame type))
        if frame_type == MCProtocol.FRAME_3E:
            data_length_index = 7
            data_start_index = 9
        else:  # FRAME_4E
            data_length_index = 3
            data_start_index = 11
        
        data_length = MCProtocol.zero_padding(hex(len(frame[data_start_index:]))[2:], 4)
        frame[data_length_index] = int(data_length[2:], 16)
        frame[data_length_index + 1] = int(data_length[0:2], 16)
        
        return bytes(frame)
    
    @staticmethod
    def create_write_frame(device_type, device_number, values, is_bit=False, frame_type=FRAME_3E, network_no=0, pc_no=0xFF, unit_io=0x03FF, unit_station=0):
        """
        書き込みフレームを作成する
        Create a write frame
        
        引数 (Arguments):
            device_type (str): デバイスタイプ ('D', 'M'など) (Device type ('D', 'M', etc.))
            device_number (int): デバイス番号 (Device number)
            values (list or int): 書き込む値のリストまたは単一の値 (List of values or a single value to write)
            is_bit (bool): ビットデバイスかどうか (Whether it's a bit device)
            frame_type (str): フレームタイプ ("3E"または"4E") (Frame type ("3E" or "4E"))
            network_no (int): ネットワーク番号 (4Eフレーム用) (Network number (for 4E frame))
            pc_no (int): PC番号 (4Eフレーム用) (PC number (for 4E frame))
            unit_io (int): ユニットI/O番号 (4Eフレーム用) (Unit I/O number (for 4E frame))
            unit_station (int): ユニット局番号 (4Eフレーム用) (Unit station number (for 4E frame))
            
        戻り値 (Returns):
            bytes: 送信用のバイナリデータ (Binary data for sending)
        """
        # デバイスタイプのチェック (Check device type)
        if device_type not in MCProtocol.DEVICE_CODES:
            raise ValueError(f"Unsupported device type: {device_type}")
        
        # フレームタイプのチェック (Check frame type)
        if frame_type not in MCProtocol.SUBHEADER:
            raise ValueError(f"Unsupported frame type: {frame_type}")
        
        # 値が単一の場合はリストに変換 (Convert a single value to a list)
        if not isinstance(values, list):
            values = [values]
        
        # コマンドの選択 (ビットデバイスかワードデバイスか) (Select command (bit device or word device))
        command = MCProtocol.CMD_BATCH_WRITE_BIT if is_bit else MCProtocol.CMD_BATCH_WRITE_WORD
        
        # フレームの共通部分を作成 (Create common part of the frame)
        frame = [
            # サブヘッダ (フレームタイプに応じて選択) (Sub-header (selected according to frame type))
            *MCProtocol.SUBHEADER[frame_type],
        ]
        
        # アクセス経路 (フレームタイプに応じて異なる) (Access path (differs according to frame type))
        if frame_type == MCProtocol.FRAME_3E:
            frame.extend([
                network_no,  # ネットワーク番号 (Network number)
                pc_no,       # PC番号 (PC number)
                unit_io & 0xFF, (unit_io >> 8) & 0xFF,  # 要求先ユニットI/O番号 (Destination unit I/O number)
                unit_station,  # 要求先ユニット局番号 (Destination unit station number)
                0x00, 0x00,  # 要求データ長 (後で設定) (Request data length (set later))
            ])
        elif frame_type == MCProtocol.FRAME_4E:
            frame.extend([
                0x00, 0x00,  # 応答データ長 (未使用) (Response data length (unused))
                0x00, 0x00,  # 要求データ長 (後で設定) (Request data length (set later))
                network_no,  # ネットワーク番号 (Network number)
                pc_no,       # PC番号 (PC number)
                0xFF, 0xFF,  # 要求先CPU監視タイマ (Destination CPU monitoring timer)
                unit_io & 0xFF, (unit_io >> 8) & 0xFF,  # 要求先ユニットI/O番号 (Destination unit I/O number)
                unit_station,  # 要求先ユニット局番号 (Destination unit station number)
            ])
        
        # 監視タイマと要求データを追加 (Add monitoring timer and request data)
        frame.extend([
            *MCProtocol.TIMER,  # 監視タイマ (Monitoring timer)
            # 要求データ (Request data)
            *command,  # コマンド (Command)
            *MCProtocol.SUBCMD,  # サブコマンド (Sub-command)
            *MCProtocol.device_number_to_bytes(device_number),  # 先頭デバイス番号 (Starting device number)
            MCProtocol.DEVICE_CODES[device_type],  # デバイスコード (Device code)
            *MCProtocol.element_to_bytes(len(values)),  # デバイス点数 (Number of device points)
        ])
        
        # 書き込む値の追加 (Add values to write)
        if is_bit:
            # ビットデバイスの場合は、1バイトで1ビットを表現 (For bit devices, 1 byte represents 1 bit)
            for value in values:
                frame.append(1 if value else 0)
        else:
            # ワードデバイスの場合は、2バイトで1ワードを表現 (For word devices, 2 bytes represent 1 word)
            for value in values:
                value_hex = MCProtocol.zero_padding(hex(value)[2:], 4)
                frame.append(int(value_hex[2:], 16))  # 下位バイト (Lower byte)
                frame.append(int(value_hex[0:2], 16))  # 上位バイト (Upper byte)
        
        # 要求データ長の設定 (フレームタイプに応じて位置が異なる) (Set request data length (position differs according to frame type))
        if frame_type == MCProtocol.FRAME_3E:
            data_length_index = 7
            data_start_index = 9
        else:  # FRAME_4E
            data_length_index = 3
            data_start_index = 11
        
        data_length = MCProtocol.zero_padding(hex(len(frame[data_start_index:]))[2:], 4)
        frame[data_length_index] = int(data_length[2:], 16)
        frame[data_length_index + 1] = int(data_length[0:2], 16)
        
        return bytes(frame)
    
    @staticmethod
    def create_write_string_frame(device_type, device_number, string_value, frame_type=FRAME_3E, network_no=0, pc_no=0xFF, unit_io=0x03FF, unit_station=0):
        """
        文字列書き込みフレームを作成する
        Create a string write frame
        
        引数 (Arguments):
            device_type (str): デバイスタイプ ('D'など) (Device type ('D', etc.))
            device_number (int): デバイス番号 (Device number)
            string_value (str): 書き込む文字列 (String to write)
            frame_type (str): フレームタイプ ("3E"または"4E") (Frame type ("3E" or "4E"))
            network_no (int): ネットワーク番号 (4Eフレーム用) (Network number (for 4E frame))
            pc_no (int): PC番号 (4Eフレーム用) (PC number (for 4E frame))
            unit_io (int): ユニットI/O番号 (4Eフレーム用) (Unit I/O number (for 4E frame))
            unit_station (int): ユニット局番号 (4Eフレーム用) (Unit station number (for 4E frame))
            
        戻り値 (Returns):
            bytes: 送信用のバイナリデータ (Binary data for sending)
        """
        # デバイスタイプのチェック (Check device type)
        if device_type not in MCProtocol.WORD_DEVICES:
            raise ValueError(f"String write is only supported for word devices: {device_type}")
        
        # フレームタイプのチェック (Check frame type)
        if frame_type not in MCProtocol.SUBHEADER:
            raise ValueError(f"Unsupported frame type: {frame_type}")
        
        # フレームの共通部分を作成 (Create common part of the frame)
        frame = [
            # サブヘッダ (フレームタイプに応じて選択) (Sub-header (selected according to frame type))
            *MCProtocol.SUBHEADER[frame_type],
        ]
        
        # アクセス経路 (フレームタイプに応じて異なる) (Access path (differs according to frame type))
        if frame_type == MCProtocol.FRAME_3E:
            frame.extend([
                network_no,  # ネットワーク番号 (Network number)
                pc_no,       # PC番号 (PC number)
                unit_io & 0xFF, (unit_io >> 8) & 0xFF,  # 要求先ユニットI/O番号 (Destination unit I/O number)
                unit_station,  # 要求先ユニット局番号 (Destination unit station number)
                0x00, 0x00,  # 要求データ長 (後で設定) (Request data length (set later))
            ])
        elif frame_type == MCProtocol.FRAME_4E:
            frame.extend([
                0x00, 0x00,  # 応答データ長 (未使用) (Response data length (unused))
                0x00, 0x00,  # 要求データ長 (後で設定) (Request data length (set later))
                network_no,  # ネットワーク番号 (Network number)
                pc_no,       # PC番号 (PC number)
                0xFF, 0xFF,  # 要求先CPU監視タイマ (Destination CPU monitoring timer)
                unit_io & 0xFF, (unit_io >> 8) & 0xFF,  # 要求先ユニットI/O番号 (Destination unit I/O number)
                unit_station,  # 要求先ユニット局番号 (Destination unit station number)
            ])
        
        # 監視タイマと要求データを追加 (Add monitoring timer and request data)
        frame.extend([
            *MCProtocol.TIMER,  # 監視タイマ (Monitoring timer)
            # 要求データ (Request data)
            *MCProtocol.CMD_BATCH_WRITE_WORD,  # コマンド (Command)
            *MCProtocol.SUBCMD,  # サブコマンド (Sub-command)
            *MCProtocol.device_number_to_bytes(device_number),  # 先頭デバイス番号 (Starting device number)
            MCProtocol.DEVICE_CODES[device_type],  # デバイスコード (Device code)
        ])
        
        # 文字列長の計算と必要なデバイス数の計算 (Calculate string length and required device count)
        # 1ワードに2バイト格納できるため、文字列長を2で割って切り上げ (1 word can store 2 bytes, so divide string length by 2 and round up)
        str_bytes = string_value.encode('utf-8')
        str_length = len(str_bytes)
        device_count = (str_length + 1) // 2  # 切り上げ (null終端用に+1) (Round up (add 1 for null termination))
        if str_length % 2 == 1:
            # 奇数バイト数の場合は、最後に1バイト（null終端）を追加 (If odd number of bytes, add 1 byte (null termination) at the end)
            str_bytes += b'\x00'
        else:
            # 偶数バイト数の場合は、最後に2バイト（null終端+パディング）を追加 (If even number of bytes, add 2 bytes (null termination + padding) at the end)
            str_bytes += b'\x00\x00'
            device_count += 1
        
        # デバイス点数の追加 (Add device count)
        frame.extend(MCProtocol.element_to_bytes(device_count))
        
        # 文字列データの追加 (リトルエンディアン：2バイトごとに逆順で格納) (Add string data (little-endian: stored in reverse order every 2 bytes))
        for i in range(0, len(str_bytes), 2):
            frame.append(str_bytes[i])
            if i + 1 < len(str_bytes):
                frame.append(str_bytes[i + 1])
            else:
                frame.append(0)  # パディング (Padding)
        
        # 要求データ長の設定 (フレームタイプに応じて位置が異なる) (Set request data length (position differs according to frame type))
        if frame_type == MCProtocol.FRAME_3E:
            data_length_index = 7
            data_start_index = 9
        else:  # FRAME_4E
            data_length_index = 3
            data_start_index = 11
        
        data_length = MCProtocol.zero_padding(hex(len(frame[data_start_index:]))[2:], 4)
        frame[data_length_index] = int(data_length[2:], 16)
        frame[data_length_index + 1] = int(data_length[0:2], 16)
        
        return bytes(frame)
    
    @staticmethod
    def parse_read_response(response, element, is_bit=False, frame_type=FRAME_3E):
        """
        読み出し応答を解析する
        Parse a read response
        
        引数 (Arguments):
            response (bytes): 受信したバイナリデータ (Received binary data)
            element (int): 読み出した要素数 (Number of elements read)
            is_bit (bool): ビットデバイスかどうか (Whether it's a bit device)
            frame_type (str): フレームタイプ ("3E"または"4E") (Frame type ("3E" or "4E"))
            
        戻り値 (Returns):
            list: 解析されたデータのリスト (List of parsed data)
        """
        # フレームタイプのチェック (Check frame type)
        if frame_type not in MCProtocol.SUBHEADER:
            raise ValueError(f"Unsupported frame type: {frame_type}")
        
        # データ開始位置の決定 (フレームタイプに応じて異なる) (Determine data start position (differs according to frame type))
        if frame_type == MCProtocol.FRAME_3E:
            data_start_index = 11  # 3Eフレームのデータ開始位置 (Data start position for 3E frame)
        else:  # FRAME_4E
            data_start_index = 15  # 4Eフレームのデータ開始位置 (Data start position for 4E frame)
        
        # エンディアン変換とデータ抽出 (Endian conversion and data extraction)
        data = []
        if is_bit:
            # ビットデバイスの場合は、1バイトで1ビットを表現 (For bit devices, 1 byte represents 1 bit)
            for i in range(data_start_index, data_start_index + element):
                data.append(response[i] != 0)
        else:
            # ワードデバイスの場合は、2バイトで1ワードを表現 (リトルエンディアン) (For word devices, 2 bytes represent 1 word (little-endian))
            for i in range(data_start_index, data_start_index + element * 2, 2):
                if i + 1 < len(response):
                    value = response[i] | (response[i + 1] << 8)
                    data.append(value)
                else:
                    # 応答データが短い場合はエラー (Error if response data is too short)
                    raise ValueError(f"Invalid response data: Data length is too short")
        
        return data
    
    @staticmethod
    def parse_string_data(word_data):
        """
        ワードデータから文字列を解析する
        Parse a string from word data
        
        引数 (Arguments):
            word_data (list): ワードデータのリスト (List of word data)
            
        戻り値 (Returns):
            str: 解析された文字列 (Parsed string)
        """
        byte_data = []
        for word in word_data:
            # ワードデータをバイトデータに変換 (リトルエンディアン) (Convert word data to byte data (little-endian))
            byte_data.append(word & 0xFF)
            byte_data.append((word >> 8) & 0xFF)
        
        # null終端までのバイトデータを取得 (Get byte data up to null termination)
        null_pos = byte_data.index(0) if 0 in byte_data else len(byte_data)
        
        # バイトデータをUTF-8文字列に変換 (Convert byte data to UTF-8 string)
        return bytes(byte_data[:null_pos]).decode('utf-8') 