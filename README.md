# Gemini Slack Bot

Slackでメンションされた質問をGoogleのGemini APIを使って回答するBotです。

## 機能

- Slack上でボットにメンションをつけて質問すると、Gemini APIを使って回答を生成します
- Socket Modeを使用してイベントを受信するため、公開URLは不要です

## セットアップ

### 前提条件

- Python 3.8以上
- Slack Bot Token
- Slack App Token (Socket Modeを有効にしたもの)
- Google Gemini API Key

### インストール手順

1. リポジトリをクローン/ダウンロード

```bash
git clone <repository-url>
cd gemini-slack-bot
```

2. 仮想環境を作成して有効化（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Unix/Mac
# または
venv\Scripts\activate  # Windows
```

3. 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

4. 環境変数を設定

`.env`ファイルを編集して、必要なトークンを設定します：

```
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
GEMINI_API_KEY=your-gemini-api-key
```

### Slackアプリの設定

1. [Slack API](https://api.slack.com/apps) でアプリを作成
2. 以下の権限（Bot Token Scopes）を追加：
   - `app_mentions:read`
   - `chat:write`
3. Socket Modeを有効化
4. アプリをワークスペースにインストール

## 使い方

1. ボットを起動

```bash
python app.py
```

2. Slackでボットにメンションをつけて質問

```
@your-bot-name 富士山の高さは？
```

## 注意事項

- API利用量に応じた料金が発生する場合があります
- Gemini APIの利用規約に従ってください# gemini-slack-bot
