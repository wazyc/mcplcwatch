"""
test_protocol.py - MCプロトコル関連機能のユニットテスト

本モジュールでは、MCプロトコルの定数とフレーム生成機能をテストします。
実際のPLC通信は行わず、生成されたフレームの形式と内容が正しいかを検証します。
"""

import unittest
from mcplcwatch.protocol import MCProtocol


class TestMCProtocol(unittest.TestCase):
    """
    MCProtocolクラスのユニットテスト
    
    テスト内容:
    - 定数の定義が正しいか
    - 3Eフレームと4Eフレームの生成が正しいか
    - ユーティリティメソッドが期待通りに動作するか
    """
    
    def test_device_codes(self):
        """
        デバイスコードの定義が正しいかテスト
        """
        # 主要なデバイスコードが定義されているか確認
        self.assertEqual(MCProtocol.DEVICE_CODES['D'], 0xA8, "Dデバイスコードが正しくありません")
        self.assertEqual(MCProtocol.DEVICE_CODES['M'], 0x90, "Mデバイスコードが正しくありません")
        self.assertEqual(MCProtocol.DEVICE_CODES['X'], 0x9C, "Xデバイスコードが正しくありません")
        self.assertEqual(MCProtocol.DEVICE_CODES['Y'], 0x9D, "Yデバイスコードが正しくありません")
    
    def test_frame_types(self):
        """
        フレームタイプの定義が正しいかテスト
        """
        self.assertEqual(MCProtocol.FRAME_3E, "3E", "3Eフレームタイプが正しくありません")
        self.assertEqual(MCProtocol.FRAME_4E, "4E", "4Eフレームタイプが正しくありません")
        
        # サブヘッダ定義が正しいか確認
        self.assertEqual(tuple(MCProtocol.SUBHEADER[MCProtocol.FRAME_3E]), (0x50, 0x00), "3Eフレームのサブヘッダが正しくありません")
        self.assertEqual(tuple(MCProtocol.SUBHEADER[MCProtocol.FRAME_4E]), (0x54, 0x00), "4Eフレームのサブヘッダが正しくありません")
    
    def test_zero_padding(self):
        """
        zero_paddingメソッドが正しく動作するかテスト
        """
        self.assertEqual(MCProtocol.zero_padding("1", 4), "0001", "0埋めが正しくありません")
        self.assertEqual(MCProtocol.zero_padding("12", 4), "0012", "0埋めが正しくありません")
        self.assertEqual(MCProtocol.zero_padding("123", 4), "0123", "0埋めが正しくありません")
        self.assertEqual(MCProtocol.zero_padding("1234", 4), "1234", "0埋めが正しくありません")
        self.assertEqual(MCProtocol.zero_padding("12345", 4), "12345", "長い文字列が切り詰められました")
    
    def test_device_number_to_bytes(self):
        """
        device_number_to_bytesメソッドが正しく動作するかテスト
        """
        # デバイス番号 100 -> 16進数で "000064" -> バイト配列 [0x64, 0x00, 0x00]
        self.assertEqual(MCProtocol.device_number_to_bytes(100), [0x64, 0x00, 0x00], "デバイス番号のバイト変換が正しくありません")
        
        # デバイス番号 1000 -> 16進数で "0003E8" -> バイト配列 [0xE8, 0x03, 0x00]
        self.assertEqual(MCProtocol.device_number_to_bytes(1000), [0xE8, 0x03, 0x00], "デバイス番号のバイト変換が正しくありません")
    
    def test_element_to_bytes(self):
        """
        element_to_bytesメソッドが正しく動作するかテスト
        """
        # 要素数 10 -> 16進数で "000A" -> バイト配列 [0x0A, 0x00]
        self.assertEqual(MCProtocol.element_to_bytes(10), [0x0A, 0x00], "要素数のバイト変換が正しくありません")
        
        # 要素数 256 -> 16進数で "0100" -> バイト配列 [0x00, 0x01]
        self.assertEqual(MCProtocol.element_to_bytes(256), [0x00, 0x01], "要素数のバイト変換が正しくありません")
    
    def test_create_3e_read_frame(self):
        """
        3Eフレームの読み出しフレーム生成が正しいかテスト
        """
        # Dデバイスの読み出しフレーム生成
        frame = MCProtocol.create_read_frame('D', 100, 10, False, MCProtocol.FRAME_3E)
        
        # フレーム形式のチェック
        self.assertIsInstance(frame, bytes, "生成されたフレームがbytes型ではありません")
        
        # サブヘッダの確認
        self.assertEqual(frame[0], 0x50, "3Eフレームのサブヘッダが正しくありません")
        self.assertEqual(frame[1], 0x00, "3Eフレームのサブヘッダが正しくありません")
        
        # コマンドの確認
        self.assertEqual(frame[11], 0x01, "読み出しコマンドが正しくありません")
        self.assertEqual(frame[12], 0x04, "読み出しコマンドが正しくありません")
        
        # デバイス番号の確認
        self.assertEqual(frame[15], 0x64, "デバイス番号のバイト[0]が正しくありません")
        self.assertEqual(frame[16], 0x00, "デバイス番号のバイト[1]が正しくありません")
        self.assertEqual(frame[17], 0x00, "デバイス番号のバイト[2]が正しくありません")
        
        # デバイスコードの確認 (位置を修正)
        self.assertEqual(frame[18], 0xA8, "デバイスコードが正しくありません")
        
        # 要素数の確認
        self.assertEqual(frame[19], 0x0A, "要素数のバイト[0]が正しくありません")
        self.assertEqual(frame[20], 0x00, "要素数のバイト[1]が正しくありません")
    
    def test_create_4e_read_frame(self):
        """
        4Eフレームの読み出しフレーム生成が正しいかテスト
        """
        # Dデバイスの読み出しフレーム生成
        frame = MCProtocol.create_read_frame('D', 100, 10, False, MCProtocol.FRAME_4E)
        
        # フレーム形式のチェック
        self.assertIsInstance(frame, bytes, "生成されたフレームがbytes型ではありません")
        
        # サブヘッダの確認
        self.assertEqual(frame[0], 0x54, "4Eフレームのサブヘッダが正しくありません")
        self.assertEqual(frame[1], 0x00, "4Eフレームのサブヘッダが正しくありません")
        
        # コマンドの確認
        self.assertEqual(frame[15], 0x01, "読み出しコマンドが正しくありません")
        self.assertEqual(frame[16], 0x04, "読み出しコマンドが正しくありません")
        
        # デバイス番号の確認
        self.assertEqual(frame[19], 0x64, "デバイス番号のバイト[0]が正しくありません")
        self.assertEqual(frame[20], 0x00, "デバイス番号のバイト[1]が正しくありません")
        self.assertEqual(frame[21], 0x00, "デバイス番号のバイト[2]が正しくありません")
        
        # デバイスコードの確認
        self.assertEqual(frame[22], 0xA8, "デバイスコードが正しくありません")
    
    def test_create_write_frame(self):
        """
        書き込みフレーム生成が正しいかテスト
        """
        # Dデバイスへの書き込みフレーム生成 (D100に12345を書き込む)
        frame = MCProtocol.create_write_frame('D', 100, 12345, False, MCProtocol.FRAME_3E)
        
        # フレーム形式のチェック
        self.assertIsInstance(frame, bytes, "生成されたフレームがbytes型ではありません")
        
        # サブヘッダの確認
        self.assertEqual(frame[0], 0x50, "3Eフレームのサブヘッダが正しくありません")
        self.assertEqual(frame[1], 0x00, "3Eフレームのサブヘッダが正しくありません")
        
        # コマンドの確認
        self.assertEqual(frame[11], 0x01, "書き込みコマンドが正しくありません")
        self.assertEqual(frame[12], 0x14, "書き込みコマンドが正しくありません")
    
    def test_parse_string_data(self):
        """
        文字列解析が正しく動作するかテスト
        """
        # "Hello" を表現するワードデータ
        # 'H'=0x48, 'e'=0x65, 'l'=0x6C, 'l'=0x6C, 'o'=0x6F, '\0'=0x00
        # リトルエンディアンなので、バイトは [0x48, 0x65] -> 0x6548
        # [0x6C, 0x6C] -> 0x6C6C, [0x6F, 0x00] -> 0x006F
        word_data = [0x6548, 0x6C6C, 0x006F]
        
        # 解析テスト
        result = MCProtocol.parse_string_data(word_data)
        self.assertEqual(result, "Hello", "文字列解析が正しくありません")
    
    def test_parse_read_response(self):
        """
        読み出し応答の解析が正しく動作するかテスト
        """
        # モック応答データ（3Eフレーム）
        # サブヘッダ(2バイト) + アクセス経路(7バイト) + 応答コード(2バイト) + データ(2バイト×5)
        mock_response_3e = bytes([
            0x50, 0x00,  # サブヘッダ
            0x00, 0xFF, 0xFF, 0x03, 0x00, 0x0A, 0x00,  # アクセス経路
            0x00, 0x00,  # 応答コード (正常)
            0x01, 0x00,  # データ1: 1
            0x02, 0x00,  # データ2: 2
            0x03, 0x00,  # データ3: 3
            0x04, 0x00,  # データ4: 4
            0x05, 0x00,  # データ5: 5
        ])
        
        # 解析テスト（3Eフレーム）
        result_3e = MCProtocol.parse_read_response(mock_response_3e, 5, False, MCProtocol.FRAME_3E)
        self.assertEqual(result_3e, [1, 2, 3, 4, 5], "3Eフレームの応答解析が正しくありません")
        
        # モック応答データ（4Eフレーム）
        # サブヘッダ(2バイト) + 応答データ長(2バイト) + 完了コード(2バイト) + 
        # アクセス経路(7バイト) + 応答コード(2バイト) + データ(2バイト×5)
        mock_response_4e = bytes([
            0x54, 0x00,  # サブヘッダ
            0x10, 0x00,  # 応答データ長
            0x00, 0x00,  # 完了コード
            0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x03, 0x00,  # アクセス経路
            0x00, 0x00,  # 応答コード (正常)
            0x01, 0x00,  # データ1: 1
            0x02, 0x00,  # データ2: 2
            0x03, 0x00,  # データ3: 3
            0x04, 0x00,  # データ4: 4
            0x05, 0x00,  # データ5: 5
        ])
        
        # 解析テスト（4Eフレーム）
        result_4e = MCProtocol.parse_read_response(mock_response_4e, 5, False, MCProtocol.FRAME_4E)
        self.assertEqual(result_4e, [1, 2, 3, 4, 5], "4Eフレームの応答解析が正しくありません")


if __name__ == '__main__':
    unittest.main() 