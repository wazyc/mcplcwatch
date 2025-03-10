# mcplcwatch テスト | mcplcwatch Tests

mcplcwatchライブラリのテストコードです。  
Test code for the mcplcwatch library.

## テストの種類 | Types of Tests

1. **単体テスト (Unit Tests)**
   - プロトコルとユーティリティ関数のテスト  
     Tests for protocol and utility functions
   - 実際のPLC通信を行わずに、関数の動作を検証  
     Verifies function behavior without actual PLC communication

2. **モックテスト (Mock Tests)**
   - 模擬的な通信を使用して、クライアントとモニタの機能をテスト  
     Tests client and monitor functionality using simulated communication
   - unittestのmockモジュールを使用して、ソケット通信をシミュレート  
     Simulates socket communication using the mock module from unittest

3. **統合テスト (Integration Tests)**
   - 実際のPLCと通信して機能をテスト  
     Tests functionality by communicating with an actual PLC
   - 実際のPLCがない場合はスキップされる  
     Skipped if no actual PLC is available

## テストの実行方法 | How to Run Tests

1. プロジェクトのルートディレクトリで以下のコマンドを実行：  
   Run the following commands in the project root directory:

```bash
# 単体テストとモックテストを実行（統合テストは含まれません）
# Run unit tests and mock tests (integration tests not included)
python run_tests.py

# 単体テストのみ実行
# Run only unit tests
python run_tests.py --unit

# モックテストのみ実行
# Run only mock tests
python run_tests.py --mock

# 統合テストのみ実行
# Run only integration tests
python run_tests.py --integration

# 読み取り専用モードで統合テストを実行（書き込みテストをスキップ）
# Run integration tests in read-only mode (skips write tests)
python run_tests.py --integration --readonly

# 詳細な出力で実行
# Run with verbose output
python run_tests.py --verbose
```

## 統合テストの設定 | Integration Test Configuration

統合テストを実行するには、以下の環境変数を設定してください：  
To run integration tests, set the following environment variables:

- `MCPLCWATCH_RUN_INTEGRATION_TESTS`: 任意の値を設定すると統合テストが実行される  
  Set to any value to run integration tests
- `MCPLCWATCH_TEST_HOST`: PLCのホスト名またはIPアドレス (デフォルト: "192.168.10.130")  
  PLC hostname or IP address (default: "192.168.10.130")
- `MCPLCWATCH_TEST_PORT`: PLCのポート番号 (デフォルト: 2000)  
  PLC port number (default: 2000)
- `MCPLCWATCH_TEST_FRAME`: フレームタイプ (デフォルト: "3E")  
  Frame type (default: "3E")

例 (Example)：

```bash
# Windows
set MCPLCWATCH_RUN_INTEGRATION_TESTS=1
set MCPLCWATCH_TEST_HOST=192.168.0.10
set MCPLCWATCH_TEST_PORT=5000
python run_tests.py --integration

# Linux/macOS
export MCPLCWATCH_RUN_INTEGRATION_TESTS=1
export MCPLCWATCH_TEST_HOST=192.168.0.10
export MCPLCWATCH_TEST_PORT=5000
python run_tests.py --integration
```

## テストカバレッジ | Test Coverage

テストカバレッジを測定するには、`coverage`パッケージを使用します：  
To measure test coverage, use the `coverage` package:

```bash
# カバレッジを計測しながらテストを実行
# Run tests while measuring coverage
coverage run run_tests.py

# レポートの表示
# Display report
coverage report

# HTMLレポートの生成
# Generate HTML report
coverage html
```

## 注意事項 | Notes

- 統合テストは、実際のPLCデバイスの値を変更します。テスト用の領域を使用してください。  
  Integration tests will change the values of actual PLC devices. Please use a test area.
- テストでは、デフォルトでデバイス番号D5000からD5010を使用します。  
  Tests use device numbers D5000 to D5010 by default.
- 統合テストは `--integration` オプションを指定した場合のみ実行されます。  
  Integration tests are only run when the `--integration` option is specified.
- PLCが接続されていない場合、統合テストは自動的にスキップされます。  
  If no PLC is connected, integration tests are automatically skipped.

### --readonlyオプションについて | About the --readonly Option

`--readonly`オプションは、PLCへの書き込み操作を行うテストをスキップします。PLC側で書き込みが禁止されている環境や、
現在動作中のPLCの値を変更したくない場合に使用してください。  
The `--readonly` option skips tests that perform write operations to the PLC. Use this option in environments where writing to the PLC is restricted, or when you don't want to change the values of a PLC that is currently in operation.

このオプションを指定すると、以下のテストがスキップされます：  
When this option is specified, the following tests will be skipped:

- `test_device_write`: デバイスへの書き込みテスト  
  `test_device_write`: Tests for writing to devices
- `test_string_operations`: 文字列操作（書き込み含む）のテスト  
  `test_string_operations`: Tests for string operations (including writing)
- `test_monitor`: モニター機能テスト（値の変更が含まれる）  
  `test_monitor`: Tests for monitor functionality (which includes changing values)

デバイスの読み取りテスト（`test_device_read`）は、PLCの現在の値を使用して実行されます。  
Device reading tests (`test_device_read`) will still run using the current values in the PLC. 