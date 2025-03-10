"""
test_client_mock.py - PLCクライアントクラスのモックテスト

本モジュールでは、実際のPLC通信をモックして、PlcClientクラスの機能をテストします。
ソケット通信をモックすることで、実際のPLCがなくてもテストができます。
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import socket
from mcplcwatch import PlcClient, PlcError, PlcTimeoutError, PlcCommunicationError, MCProtocol


class TestPlcClientMock(unittest.TestCase):
    """
    PlcClientクラスのモックテスト
    
    テスト内容:
    - 接続処理が正しいか
    - 読み書きメソッドが正しく動作するか
    - エラー処理が適切か
    """
    
    @patch('socket.socket')
    def test_connection(self, mock_socket):
        """
        接続処理のテスト
        """
        # ソケットのモックを設定
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # クライアントインスタンスを作成
        client = PlcClient(host="192.168.0.1", port=5000)
        
        # 接続処理が正しく行われたかチェック
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket_instance.connect.assert_called_once_with(("192.168.0.1", 5000))
        mock_socket_instance.settimeout.assert_called_once_with(1.0)
        
        # クライアントのクローズ
        client.close()
        mock_socket_instance.close.assert_called_once()
    
    @patch('socket.socket')
    def test_connection_error(self, mock_socket):
        """
        接続エラー処理のテスト
        """
        # ソケットのモックを設定して例外を発生させる
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = socket.error("Connection refused")
        
        # 接続エラーが例外として捕捉されることを確認
        with self.assertRaises(PlcCommunicationError):
            client = PlcClient(host="192.168.0.1", port=5000)
    
    @patch('socket.socket')
    def test_read_device(self, mock_socket):
        """
        read_deviceメソッドのテスト
        """
        # ソケットのモックを設定
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # レスポンスデータを設定（3Eフレーム）
        mock_response = bytes([
            0x50, 0x00,  # サブヘッダ
            0x00, 0xFF, 0xFF, 0x03, 0x00, 0x0A, 0x00,  # アクセス経路
            0x00, 0x00,  # 応答コード (正常)
            0x2A, 0x00,  # データ: 42
        ])
        mock_socket_instance.recv.return_value = mock_response
        
        # クライアントインスタンスを作成
        client = PlcClient(host="192.168.0.1", port=5000)
        
        # Dデバイスの値を読み出し
        result = client.read_device('D', 100)
        
        # 送信データの確認
        mock_socket_instance.sendall.assert_called_once()
        send_args = mock_socket_instance.sendall.call_args[0][0]
        self.assertEqual(send_args[0:2], bytes([0x50, 0x00]), "送信データのサブヘッダが正しくありません")
        
        # 読み出し結果の確認
        self.assertEqual(result, 42, "読み出し結果が正しくありません")
        
        # クライアントのクローズ
        client.close()
    
    @patch('socket.socket')
    def test_write_device(self, mock_socket):
        """
        write_deviceメソッドのテスト
        """
        # ソケットのモックを設定
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # レスポンスデータを設定（3Eフレーム）
        mock_response = bytes([
            0x50, 0x00,  # サブヘッダ
            0x00, 0xFF, 0xFF, 0x03, 0x00, 0x02, 0x00,  # アクセス経路
            0x00, 0x00,  # 応答コード (正常)
        ])
        mock_socket_instance.recv.return_value = mock_response
        
        # クライアントインスタンスを作成
        client = PlcClient(host="192.168.0.1", port=5000)
        
        # Dデバイスに値を書き込み
        result = client.write_device('D', 100, 42)
        
        # 送信データの確認
        mock_socket_instance.sendall.assert_called_once()
        send_args = mock_socket_instance.sendall.call_args[0][0]
        self.assertEqual(send_args[0:2], bytes([0x50, 0x00]), "送信データのサブヘッダが正しくありません")
        
        # 書き込み結果の確認
        self.assertTrue(result, "書き込み結果が正しくありません")
        
        # クライアントのクローズ
        client.close()
    
    @patch('socket.socket')
    def test_read_timeout(self, mock_socket):
        """
        タイムアウトエラー処理のテスト
        """
        # ソケットのモックを設定して例外を発生させる
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.side_effect = socket.timeout("Timeout")
        
        # クライアントインスタンスを作成
        client = PlcClient(host="192.168.0.1", port=5000)
        
        # タイムアウトエラーが例外として捕捉されることを確認
        with self.assertRaises(PlcTimeoutError):
            result = client.read_device('D', 100)
        
        # 接続状態がリセットされていることを確認
        self.assertFalse(client.connected, "タイムアウト後に接続状態がリセットされていません")
        
        # クライアントのクローズ
        client.close()
    
    @patch('socket.socket')
    def test_error_response(self, mock_socket):
        """
        エラーレスポンス処理のテスト
        """
        # ソケットのモックを設定
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # エラーレスポンスデータを設定（3Eフレーム、エラーコード0xC059）
        mock_response = bytes([
            0x50, 0x00,  # サブヘッダ
            0x00, 0xFF, 0xFF, 0x03, 0x00, 0x02, 0x00,  # アクセス経路
            0x59, 0xC0,  # 応答コード (エラー: 0xC059)
        ])
        mock_socket_instance.recv.return_value = mock_response
        
        # クライアントインスタンスを作成
        client = PlcClient(host="192.168.0.1", port=5000)
        
        # デバイスエラーが例外として捕捉されることを確認
        with self.assertRaises(PlcError):
            result = client.read_device('D', 100)
        
        # クライアントのクローズ
        client.close()
    
    @patch('socket.socket')
    def test_frame_type_selection(self, mock_socket):
        """
        フレームタイプ選択のテスト
        """
        # ソケットのモックを設定
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # 3Eフレームレスポンスデータを設定
        mock_response_3e = bytes([
            0x50, 0x00,  # サブヘッダ
            0x00, 0xFF, 0xFF, 0x03, 0x00, 0x0A, 0x00,  # アクセス経路
            0x00, 0x00,  # 応答コード (正常)
            0x2A, 0x00,  # データ: 42
        ])
        
        # 4Eフレームレスポンスデータを設定
        mock_response_4e = bytes([
            0x54, 0x00,  # サブヘッダ
            0x11, 0x00,  # 応答データ長（17バイト）
            0x00, 0x00,  # 完了コード (offset 4-5)
            0x00, 0x00,  # ネットワーク番号、PC番号 (offset 6-7)
            0xFF, 0x03, 0x00, 0x00,  # 要求先ユニットI/O番号、要求先ユニット局番号 (offset 8-11)
            0x00, 0x00,  # 応答コード (正常) (offset 12-13)
            0x00, 0x2A,  # データ: 10752 (リトルエンディアン、offset 14-15)
            0x00, 0x00   # 予備領域 (offset 16-17)
        ])
        
        # 3Eフレームでのテスト
        mock_socket_instance.recv.return_value = mock_response_3e
        client_3e = PlcClient(host="192.168.0.1", port=5000, frame_type=MCProtocol.FRAME_3E)
        result_3e = client_3e.read_device('D', 100)
        self.assertEqual(result_3e, 42, "3Eフレームでの読み出し結果が正しくありません")
        send_args_3e = mock_socket_instance.sendall.call_args[0][0]
        self.assertEqual(send_args_3e[0:2], bytes([0x50, 0x00]), "3Eフレームの送信データが正しくありません")
        client_3e.close()
        
        # 4Eフレームでのテスト
        mock_socket.reset_mock()
        mock_socket_instance.reset_mock()
        mock_socket_instance.recv.return_value = mock_response_4e
        client_4e = PlcClient(host="192.168.0.1", port=5000, frame_type='4E')
        result_4e = client_4e.read_device('D', 100)
        self.assertEqual(result_4e, 42, "4Eフレームでの読み出し結果が正しくありません")  # 0x002A = 42
        send_args_4e = mock_socket_instance.sendall.call_args[0][0]
        self.assertEqual(send_args_4e[0:2], bytes([0x54, 0x00]), "4Eフレームの送信データが正しくありません")
        client_4e.close()


if __name__ == '__main__':
    unittest.main() 