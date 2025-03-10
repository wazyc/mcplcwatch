"""
test_integration.py - 実際のPLCとの統合テスト

本モジュールでは、実際のPLCと通信して、ライブラリの機能を確認します。
実際のPLCが接続されていない場合は、テストをスキップします。
"""

import unittest
import time
import os
import sys
from mcplcwatch import PlcClient, PlcMonitor, PlcError, MCProtocol

# テスト用PLC情報
PLC_HOST = os.getenv('MCPLCWATCH_TEST_HOST', '192.168.10.130')
PLC_PORT = int(os.getenv('MCPLCWATCH_TEST_PORT', '5000'))
PLC_FRAME_TYPE = os.getenv('MCPLCWATCH_TEST_FRAME', MCProtocol.FRAME_3E)

# テストデバイス情報
TEST_DEVICE_TYPE = 'D'
TEST_DEVICE_START = 1000  # テスト用に使用するデバイスの開始番号
TEST_DEVICE_COUNT = 10    # テスト用に使用するデバイスの数

# 読み取り専用モードかどうか
READONLY_MODE = os.getenv('MCPLCWATCH_READONLY_TESTS') is not None

@unittest.skipUnless(os.getenv('MCPLCWATCH_RUN_INTEGRATION_TESTS'), 'PLCとの統合テストをスキップします')
class TestPlcIntegration(unittest.TestCase):
    """
    PLCとの統合テスト
    
    テスト内容:
    - 実際のPLCとの接続
    - データの読み書き
    - 監視機能
    
    注意:
    - このテストを実行するには、環境変数 MCPLCWATCH_RUN_INTEGRATION_TESTS を設定してください
    - PLC接続情報は環境変数で設定できます:
      - MCPLCWATCH_TEST_HOST: PLCのホスト名またはIPアドレス
      - MCPLCWATCH_TEST_PORT: PLCのポート番号
      - MCPLCWATCH_TEST_FRAME: フレームタイプ ('3E' または '4E')
    """
    
    @classmethod
    def setUpClass(cls):
        """
        テストの前処理
        """
        try:
            print(f"PLCとの統合テストを開始します: {PLC_HOST}:{PLC_PORT} ({PLC_FRAME_TYPE}フレーム)")
            
            # PLC接続
            cls.plc = PlcClient(host=PLC_HOST, port=PLC_PORT, frame_type=PLC_FRAME_TYPE)
            
            # 接続確認
            test_value = cls.plc.read_device(TEST_DEVICE_TYPE, TEST_DEVICE_START)
            print(f"PLC接続確認: {TEST_DEVICE_TYPE}{TEST_DEVICE_START} = {test_value}")
            
            # テスト用の初期値を設定
            if not READONLY_MODE:
                # 読み取り専用モードでない場合のみ初期化を実行
                for i in range(TEST_DEVICE_COUNT):
                    cls.plc.write_device(TEST_DEVICE_TYPE, TEST_DEVICE_START + i, i)
                print("テスト用データの初期化が完了しました")
            else:
                print("読み取り専用モードのため、データの初期化をスキップします")
            
        except Exception as e:
            print(f"PLCとの接続に失敗しました: {e}")
            raise
    
    @classmethod
    def tearDownClass(cls):
        """
        テストクラスの終了処理
        """
        if cls.plc:
            cls.plc.close()
            print("PLCとの接続を閉じました")
    
    def setUp(self):
        """
        各テストの前処理
        """
        # PLCが接続されていることを確認
        if not self.plc:
            self.skipTest("PLCが接続されていません")
    
    def test_device_read(self):
        """
        デバイス読み出しテスト
        """
        # 単一デバイスの読み出し
        value = self.plc.read_device(TEST_DEVICE_TYPE, TEST_DEVICE_START)
        # PLC側の実際の値を検証します
        print(f"{TEST_DEVICE_TYPE}{TEST_DEVICE_START}の現在値: {value}")
        self.assertIsNotNone(value, f"{TEST_DEVICE_TYPE}{TEST_DEVICE_START}の値が読み出せません")
        
        # 複数デバイスの読み出し
        values = self.plc.read_devices(TEST_DEVICE_TYPE, TEST_DEVICE_START, 5)
        self.assertEqual(len(values), 5, "読み出されたデバイス数が正しくありません")
        # PLC側の実際の値を表示します
        for i, value in enumerate(values):
            print(f"{TEST_DEVICE_TYPE}{TEST_DEVICE_START + i}の現在値: {value}")
            self.assertIsNotNone(value, f"{TEST_DEVICE_TYPE}{TEST_DEVICE_START + i}の値が読み出せません")
    
    @unittest.skipIf(READONLY_MODE, "読み取り専用モードのため、書き込みテストをスキップします")
    def test_device_write(self):
        """
        デバイス書き込みテスト
        """
        # 単一デバイスの書き込み
        test_value = 12345
        self.plc.write_device(TEST_DEVICE_TYPE, TEST_DEVICE_START, test_value)
        
        # 書き込んだ値を読み出して検証
        value = self.plc.read_device(TEST_DEVICE_TYPE, TEST_DEVICE_START)
        self.assertEqual(value, test_value, "書き込んだ値が正しく読み出せません")
        
        # 複数デバイスの書き込み
        test_values = [100, 200, 300, 400, 500]
        self.plc.write_devices(TEST_DEVICE_TYPE, TEST_DEVICE_START, test_values)
        
        # 書き込んだ値を読み出して検証
        values = self.plc.read_devices(TEST_DEVICE_TYPE, TEST_DEVICE_START, len(test_values))
        self.assertEqual(values, test_values, "書き込んだ値が正しく読み出せません")
        
        # テスト後の初期化
        for i in range(TEST_DEVICE_COUNT):
            self.plc.write_device(TEST_DEVICE_TYPE, TEST_DEVICE_START + i, i)
    
    @unittest.skipIf(READONLY_MODE, "読み取り専用モードのため、文字列書き込みテストをスキップします")
    def test_string_operations(self):
        """
        文字列操作テスト
        """
        # 文字列の書き込み
        test_string = "にほんご書込みテスト"
        self.plc.write_string(TEST_DEVICE_TYPE, TEST_DEVICE_START + 50, test_string)
        
        # 文字列の読み出し
        read_string = self.plc.read_string(TEST_DEVICE_TYPE, TEST_DEVICE_START + 50)
        self.assertEqual(read_string, test_string, "書き込んだ文字列が正しく読み出せません")
    
    @unittest.skipIf(READONLY_MODE, "読み取り専用モードのため、モニターテストをスキップします")
    def test_monitor(self):
        """
        監視機能テスト
        """
        # 値変更検出フラグ
        value_changed = False
        changed_value = None
        
        # コールバック関数
        def on_change(device_type, device_number, old_value, new_value):
            nonlocal value_changed, changed_value
            value_changed = True
            changed_value = new_value
            print(f"{device_type}{device_number} が {old_value} から {new_value} に変更されました")
        
        # モニターの設定
        monitor = PlcMonitor(self.plc, interval=0.5)
        monitor.add_device(TEST_DEVICE_TYPE, TEST_DEVICE_START, callback=on_change)
        
        # 初期値を設定
        self.plc.write_device(TEST_DEVICE_TYPE, TEST_DEVICE_START, 0)
        
        # 監視開始
        monitor.start()
        
        try:
            # 最初のポーリングが完了するまで待機
            time.sleep(1.0)
            
            # 値を変更
            self.plc.write_device(TEST_DEVICE_TYPE, TEST_DEVICE_START, 9999)
            
            # 変更が検出されるまで待機
            timeout = time.time() + 2.0  # 2秒のタイムアウト
            while not value_changed and time.time() < timeout:
                time.sleep(0.1)
            
            # 値の変更が検出されたかチェック
            self.assertTrue(value_changed, "値の変更が検出されませんでした")
            self.assertEqual(changed_value, 9999, "検出された値が正しくありません")
            
        finally:
            # 監視停止
            monitor.stop()
            
            # テスト後の初期化
            self.plc.write_device(TEST_DEVICE_TYPE, TEST_DEVICE_START, 0)


if __name__ == '__main__':
    unittest.main() 