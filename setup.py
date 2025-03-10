"""
setup.py - mcplcwatchパッケージのインストール設定ファイル

本ファイルは、mcplcwatchパッケージをインストールするための設定を記述しています。
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcplcwatch",
    version="0.1.0",
    author="wazyc",
    author_email="user@example.com",
    description="MCプロトコルを使用してPLCのデータを読み書き、監視するライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/user/mcplcwatch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[],
    keywords=["plc", "mc protocol", "mitsubishi", "industrial", "automation", "scada", "iot"],
    project_urls={
        "Bug Reports": "https://github.com/user/mcplcwatch/issues",
        "Source": "https://github.com/user/mcplcwatch",
    },
) 