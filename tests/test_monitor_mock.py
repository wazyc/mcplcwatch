"""
test_monitor_mock.py - PLCモニタークラスのモックテスト

本モジュールでは、実際のPLC通信をモックして、PlcMonitorクラスの機能をテストします。
モニター機能の動作とコールバック処理をテストします。
"""

import unittest
from unittest.mock import patch, Mock, MagicMock, call
import time
import threading
from mcplcwatch import PlcClient, PlcMonitor, PlcError


class TestPlcMonitorMock(unittest.TestCase):
    """
    PlcMonitorクラスのモックテスト
    
    テスト内容:
    - モニターの初期化と設定が正しいか
    - デバイス監視の追加と削除が正しく動作するか
    - 値の変更検出とコールバック処理が正しく動作するか
    """
    
    def setUp(self):
        """
        テスト前の準備
        """
        # PLCクライアントのモック作成
        self.mock_plc = MagicMock(spec=PlcClient)
        
        # read_device/read_devicesの戻り値を設定
        self.mock_plc.read_device.return_value = 0
        self.mock_plc.read_devices.return_value = [0, 0, 0]
    
    def test_monitor_initialization(self):
        """
        モニター初期化のテスト
        """
        # モニターインスタンスを作成
        monitor = PlcMonitor(self.mock_plc)
        
        # 初期状態のチェック
        self.assertEqual(monitor.plc, self.mock_plc, "PLCクライアントの参照が正しくありません")
        self.assertEqual(monitor.interval, 1.0, "デフォルトの監視間隔が正しくありません")
        self.assertFalse(monitor.running, "初期状態で実行中になっています")
        self.assertIsNone(monitor.thread, "初期状態でスレッドが存在しています")
        self.assertEqual(len(monitor.monitors), 0, "初期状態で監視対象が存在しています")
        self.assertEqual(len(monitor.group_monitors), 0, "初期状態でグループ監視対象が存在しています")
    
    def test_add_device(self):
        """
        デバイス監視追加のテスト
        """
        # モニターインスタンスを作成
        monitor = PlcMonitor(self.mock_plc)
        
        # コールバック関数を作成
        callback = MagicMock()
        error_callback = MagicMock()
        
        # デバイス監視を追加
        device_monitor = monitor.add_device('D', 100, callback, error_callback)
        
        # 監視対象が追加されたかチェック
        self.assertEqual(len(monitor.monitors), 1, "監視対象が追加されていません")
        self.assertEqual(monitor.monitors[0], device_monitor, "追加された監視対象が正しくありません")
        
        # デバイスモニターの設定をチェック
        self.assertEqual(device_monitor.device_type, 'D', "デバイスタイプが正しくありません")
        self.assertEqual(device_monitor.device_number, 100, "デバイス番号が正しくありません")
        self.assertEqual(device_monitor.callback, callback, "コールバック関数が正しくありません")
        self.assertEqual(device_monitor.on_error, error_callback, "エラーコールバック関数が正しくありません")
        
        # 初期値の読み込みが行われたかチェック
        self.mock_plc.read_device.assert_called_once_with('D', 100)
        self.assertEqual(device_monitor.last_value, 0, "初期値が正しくありません")
    
    def test_add_devices(self):
        """
        デバイスグループ監視追加のテスト
        """
        # モニターインスタンスを作成
        monitor = PlcMonitor(self.mock_plc)
        
        # コールバック関数を作成
        callback = MagicMock()
        error_callback = MagicMock()
        
        # デバイスグループ監視を追加
        group_monitor = monitor.add_devices('D', 100, 3, callback, error_callback)
        
        # 監視対象が追加されたかチェック
        self.assertEqual(len(monitor.group_monitors), 1, "グループ監視対象が追加されていません")
        self.assertEqual(monitor.group_monitors[0], group_monitor, "追加されたグループ監視対象が正しくありません")
        
        # グループモニターの設定をチェック
        self.assertEqual(group_monitor.device_type, 'D', "デバイスタイプが正しくありません")
        self.assertEqual(group_monitor.start_number, 100, "開始デバイス番号が正しくありません")
        self.assertEqual(group_monitor.count, 3, "デバイス数が正しくありません")
        self.assertEqual(group_monitor.callback, callback, "コールバック関数が正しくありません")
        self.assertEqual(group_monitor.on_error, error_callback, "エラーコールバック関数が正しくありません")
        
        # 初期値の読み込みが行われたかチェック
        self.mock_plc.read_devices.assert_called_once_with('D', 100, 3)
        self.assertEqual(group_monitor.last_values, [0, 0, 0], "初期値が正しくありません")
    
    def test_remove_device(self):
        """
        デバイス監視削除のテスト
        """
        # モニターインスタンスを作成
        monitor = PlcMonitor(self.mock_plc)
        
        # デバイス監視を追加
        monitor.add_device('D', 100)
        monitor.add_device('D', 200)
        
        # 削除前の監視対象数を確認
        self.assertEqual(len(monitor.monitors), 2, "監視対象の追加が正しく動作していません")
        
        # デバイス監視を削除
        result = monitor.remove_device('D', 100)
        
        # 削除結果をチェック
        self.assertTrue(result, "削除に失敗しました")
        self.assertEqual(len(monitor.monitors), 1, "監視対象が削除されていません")
        self.assertEqual(monitor.monitors[0].device_number, 200, "誤った監視対象が削除されました")
        
        # 存在しないデバイス監視の削除テスト
        result = monitor.remove_device('D', 300)
        self.assertFalse(result, "存在しないデバイス監視の削除が成功しました")
    
    def test_remove_devices(self):
        """
        デバイスグループ監視削除のテスト
        """
        # モニターインスタンスを作成
        monitor = PlcMonitor(self.mock_plc)
        
        # デバイスグループ監視を追加
        monitor.add_devices('D', 100, 3)
        monitor.add_devices('D', 200, 5)
        
        # 削除前の監視対象数を確認
        self.assertEqual(len(monitor.group_monitors), 2, "グループ監視対象の追加が正しく動作していません")
        
        # デバイスグループ監視を削除
        result = monitor.remove_devices('D', 100, 3)
        
        # 削除結果をチェック
        self.assertTrue(result, "削除に失敗しました")
        self.assertEqual(len(monitor.group_monitors), 1, "グループ監視対象が削除されていません")
        self.assertEqual(monitor.group_monitors[0].start_number, 200, "誤ったグループ監視対象が削除されました")
        
        # 存在しないデバイスグループ監視の削除テスト
        result = monitor.remove_devices('D', 300, 2)
        self.assertFalse(result, "存在しないグループ監視対象の削除が成功しました")
    
    def test_clear(self):
        """
        監視対象クリアのテスト
        """
        # モニターインスタンスを作成
        monitor = PlcMonitor(self.mock_plc)
        
        # 監視対象を追加
        monitor.add_device('D', 100)
        monitor.add_devices('D', 200, 3)
        
        # クリア前の監視対象数を確認
        self.assertEqual(len(monitor.monitors), 1, "デバイス監視対象の追加が正しく動作していません")
        self.assertEqual(len(monitor.group_monitors), 1, "グループ監視対象の追加が正しく動作していません")
        
        # 監視対象をクリア
        monitor.clear()
        
        # クリア後の監視対象数を確認
        self.assertEqual(len(monitor.monitors), 0, "デバイス監視対象がクリアされていません")
        self.assertEqual(len(monitor.group_monitors), 0, "グループ監視対象がクリアされていません")
    
    def test_start_stop(self):
        """
        監視の開始と停止のテスト
        """
        # モニターインスタンスを作成
        monitor = PlcMonitor(self.mock_plc)
        
        # 監視開始
        monitor.start(interval=0.1)
        
        # 実行状態のチェック
        self.assertTrue(monitor.running, "監視が開始されていません")
        self.assertIsNotNone(monitor.thread, "スレッドが作成されていません")
        self.assertEqual(monitor.interval, 0.1, "監視間隔が設定されていません")
        
        # 監視停止
        monitor.stop()
        
        # 停止状態のチェック
        self.assertFalse(monitor.running, "監視が停止されていません")
    
    def test_device_value_change(self):
        """
        デバイス値変更検出のテスト
        """
        # モニターインスタンスを作成
        callback = MagicMock()
        monitor = PlcMonitor(self.mock_plc)
        
        # デバイス監視を追加
        device_monitor = monitor.add_device('D', 100, callback)
        
        # 初期値を設定
        device_monitor.last_value = 10
        
        # 値の変更をシミュレート
        device_monitor.update(20)
        
        # コールバック呼び出しをチェック
        callback.assert_called_once_with('D', 100, 10, 20)
        
        # 更新後の値をチェック
        self.assertEqual(device_monitor.last_value, 20, "値が更新されていません")
    
    def test_group_value_change(self):
        """
        デバイスグループ値変更検出のテスト
        """
        # モニターインスタンスを作成
        callback = MagicMock()
        monitor = PlcMonitor(self.mock_plc)
        
        # デバイスグループ監視を追加
        group_monitor = monitor.add_devices('D', 100, 3, callback)
        
        # 初期値を設定
        group_monitor.last_values = [10, 20, 30]
        
        # 値の変更をシミュレート
        group_monitor.update([10, 25, 30])
        
        # コールバック呼び出しをチェック (D101の値のみが変更)
        callback.assert_called_once_with('D', 101, 20, 25)
        
        # 更新後の値をチェック
        self.assertEqual(group_monitor.last_values, [10, 25, 30], "値が更新されていません")
    
    def test_error_handling(self):
        """
        エラーハンドリングのテスト
        """
        # モニターインスタンスを作成
        error_callback = MagicMock()
        monitor = PlcMonitor(self.mock_plc)
        
        # デバイス監視を追加
        device_monitor = monitor.add_device('D', 100, on_error=error_callback)
        
        # エラーを発生させる
        error = PlcError("テストエラー")
        device_monitor.handle_error(error)
        
        # エラーコールバック呼び出しをチェック
        error_callback.assert_called_once_with('D', 100, error)


if __name__ == '__main__':
    unittest.main() 