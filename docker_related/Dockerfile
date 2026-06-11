# 使用輕量級 Python
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /upotserver

# 先複製依賴清單以利用 Docker 快取
COPY requirements.txt .

# 安裝必要的套件 
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update
RUN apt-get -y install procps
RUN apt-get -y install net-tools