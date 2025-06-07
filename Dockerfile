FROM alpine:3.18

# 必要なパッケージをインストール
RUN apk add --no-cache python3 py3-pip python3-dev

# 作業ディレクトリを設定
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt .
COPY app.py .

# venvを作成して有効化し、パッケージをインストール
RUN python3 -m venv /app/venv
# シェルを使用してvenvをアクティベート
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# 環境変数を設定
ENV PATH="/app/venv/bin:$PATH"

# アプリケーションを実行
CMD ["python3", "app.py"]
