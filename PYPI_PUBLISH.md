# PyPIへのパッケージ公開手順

このドキュメントでは、mcplcwatchパッケージをPyPI（Python Package Index）に公開する手順を説明します。

## 前提条件

1. PyPIアカウントの作成
2. 必要なPythonパッケージのインストール

## 1. PyPIアカウントの作成

1. [PyPI](https://pypi.org/account/register/)にアクセスしてアカウントを作成します。
2. メールで送られてくる確認リンクをクリックして、アカウントを有効化します。
3. 二要素認証（2FA）の設定を行うことを強くお勧めします。

## 2. 必要なパッケージのインストール

```bash
pip install build twine
```

## 3. ビルドとアップロード手順

### ビルドの実行

以下のコマンドを実行して、配布用のパッケージをビルドします：

```bash
python -m build
```

これにより、`dist/`ディレクトリにSDist（.tar.gz）とWheel（.whl）の両方のパッケージが作成されます。

### PyPIへのアップロード

#### TestPyPI（テスト環境）へのアップロード（推奨）

まず、本番環境にアップロードする前に、TestPyPIでテストすることをお勧めします：

```bash
twine upload --repository testpypi dist/*
```

TestPyPIからインストールするには：

```bash
pip install --index-url https://test.pypi.org/simple/ mcplcwatch
```

#### 本番PyPIへのアップロード

テストが完了したら、本番環境へアップロードします：

```bash
twine upload dist/*
```

アップロード時にPyPIのユーザー名とパスワードが求められます。

## 4. バージョンアップデート方法

1. `mcplcwatch/__init__.py`の`__version__`を更新
2. `pyproject.toml`の`version`を更新
3. 変更履歴を更新（オプションですが推奨）
4. 上記の「ビルドとアップロード手順」を再度実行

## 5. トラブルシューティング

- バージョン番号は既存のものと異なる必要があります
- PyPIでは一度アップロードしたパッケージは変更できません
- ユーザー名やパスワードに問題がある場合は、`~/.pypirc`ファイルを設定するか、環境変数を使用してください

## 参考リンク

- [PyPI公式ドキュメント](https://packaging.python.org/tutorials/packaging-projects/)
- [TestPyPI](https://test.pypi.org/)
- [Twineドキュメント](https://twine.readthedocs.io/en/latest/) 