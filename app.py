#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import google.generativeai as genai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from markdown_to_mrkdwn import SlackMarkdownConverter

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SlackのAPI設定
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

# GeminiのAPI設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# モデル設定（最新のGemini Proモデルを使用）
model = genai.GenerativeModel('gemini-2.0-flash')

converter = SlackMarkdownConverter()

# Slackアプリの初期化
app = App(token=SLACK_BOT_TOKEN)

def get_gemini_response(prompt):
    """
    GeminiにプロンプトをPOSTして回答を取得する
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"申し訳ありませんが、エラーが発生しました: {e}"

@app.event("app_mention")
def handle_mention(event, say):
    """
    メンションされたときに実行される処理
    """
    user_id = event["user"]
    text = event["text"]
    thread_ts = event.get("thread_ts", event["ts"])

    # メンション部分を除いたテキストを取得
    # 例: <@U123456> こんにちは → こんにちは
    prompt = text.split(">", 1)[1].strip() if ">" in text else text

    if not prompt:
        say(thread_ts=thread_ts, text=f"<@{user_id}> 何かご質問はありますか？")
        return

    logger.info(f"Received question: {prompt}")

    # 処理中メッセージ
    say(thread_ts=thread_ts, text=f"Generating...")

    # Geminiから回答を取得
    response = get_gemini_response(prompt)

    # 回答を返信
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<@{user_id}>\n{prompt}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": converter.convert(response)
            }
        }
    ]
    say(thread_ts=thread_ts, blocks=blocks)

if __name__ == "__main__":
    try:
        logger.info("Starting the app...")
        if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not GEMINI_API_KEY:
            logger.error("必要な環境変数が設定されていません。.envファイルを確認してください。")
            exit(1)

        # Socket Mode
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
    except Exception as e:
        logger.error(f"Error starting app: {e}")
