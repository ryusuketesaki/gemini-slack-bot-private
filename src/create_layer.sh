#!/bin/bash

# クリーンアップ
rm -rf lambda_layer
rm -f lambda_layer.zip

# レイヤー用のディレクトリを作成
mkdir -p lambda_layer/python

# パッケージをインストール
pip install -r requirements.txt -t lambda_layer/python

# 不要なファイルを削除
cd lambda_layer/python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
find . -type d -name "tests" -exec rm -rf {} +
find . -type d -name "test" -exec rm -rf {} +
find . -type d -name "docs" -exec rm -rf {} +
find . -type d -name "examples" -exec rm -rf {} +

# ZIPファイルを作成
cd ../
zip -r9 ../lambda_layer.zip .
