#!/bin/bash

# 創建目錄，用於存放測試覆蓋率報告
mkdir -p tests/coverage

# 安裝測試和覆蓋率相關的 Python 包
python -m pip install pytest coverage pytest-cov

# 執行 pytest 進行測試，並使用 pytest-cov 插件生成覆蓋率報告
python -m pytest -x --cov=textgenerator tests

# 生成詳細的覆蓋率報告，並將報告輸出到指定文件中
coverage report -m | tee tests/coverage/cov.txt
