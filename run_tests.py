#!/usr/bin/env python
"""
run_tests.py - mcplcwatchのテストを実行するスクリプト

使用方法:
  python run_tests.py [オプション]

オプション:
  --unit       単体テストのみ実行
  --mock       モックテストのみ実行
  --integration 統合テストのみ実行
  --all        単体テストとモックテストを実行 (デフォルト、統合テストは含まれません)
  --verbose    詳細な出力
"""

import unittest
import sys
import os
import argparse


def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='mcplcwatchのテストを実行します')
    parser.add_argument('--unit', action='store_true', help='単体テストのみ実行')
    parser.add_argument('--mock', action='store_true', help='モックテストのみ実行')
    parser.add_argument('--integration', action='store_true', help='統合テストのみ実行')
    parser.add_argument('--all', action='store_true', help='単体テストとモックテストを実行（統合テストは含まれません）')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細な出力')
    args = parser.parse_args()
    
    # オプションが指定されていない場合は --all を設定
    if not (args.unit or args.mock or args.integration or args.all):
        args.all = True
    
    # verboseの設定
    verbosity = 2 if args.verbose else 1
    
    # テストスイートの作成
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # 実行するテストの指定
    if args.all or args.unit:
        unit_tests = loader.discover('tests', pattern='test_protocol.py')
        test_suite.addTest(unit_tests)
        print("単体テストを追加しました")
    
    if args.all or args.mock:
        mock_tests = loader.discover('tests', pattern='test_*_mock.py')
        test_suite.addTest(mock_tests)
        print("モックテストを追加しました")
    
    # 統合テストは--integrationオプションが明示的に指定された場合のみ実行
    if args.integration:
        # 統合テストを実行する場合は環境変数を設定
        os.environ['MCPLCWATCH_RUN_INTEGRATION_TESTS'] = '1'
        integration_tests = loader.discover('tests', pattern='test_integration.py')
        test_suite.addTest(integration_tests)
        print("統合テストを追加しました")
    
    # テストの実行
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)
    
    # 終了コードの設定
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main() 