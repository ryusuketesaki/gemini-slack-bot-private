import os
import json
import logging
import boto3
from datetime import datetime
import google.generativeai as genai
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DynamoDB設定
dynamodb = boto3.resource('dynamodb')
usage_table = dynamodb.Table('GeminiApiUsage')

# 環境変数から制限値を取得
DAILY_LIMIT = int(os.environ.get('GEMINI_DAILY_LIMIT', '1000'))

# SlackのAPI設定
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]

# GeminiのAPI設定
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# モデル設定
model = genai.GenerativeModel('gemini-2.0-flash')

# Slackアプリの初期化
app = App(token=SLACK_BOT_TOKEN, process_before_response=True)

def check_api_limit() -> bool:
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        response = usage_table.update_item(
            Key={'date': today},
            UpdateExpression='ADD usage_count :inc',
            ExpressionAttributeValues={':inc': 1},
            ReturnValues='UPDATED_NEW'
        )
        current_count = response['Attributes']['usage_count']
        return current_count <= DAILY_LIMIT
    except Exception as e:
        logger.error(f"API limit check error: {e}")
        return True

def get_gemini_response(prompt):
    if not check_api_limit():
        return "申し訳ありませんが、本日のAPI利用制限に達しました。明日以降に再度お試しください。"

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"申し訳ありませんが、エラーが発生しました: {e}"

@app.event("app_mention")
def handle_mention(event, say):
    user_id = event["user"]
    text = event["text"]
    thread_ts = event.get("thread_ts", event["ts"])

    prompt = text.split(">", 1)[1].strip() if ">" in text else text

    if not prompt:
        say(thread_ts=thread_ts, text=f"<@{user_id}> 何かご質問はありますか？")
        return

    logger.info(f"Received question: {prompt}")
    say(thread_ts=thread_ts, text=f"Generating...")

    response = get_gemini_response(prompt)

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
                "text": response
            }
        }
    ]
    say(thread_ts=thread_ts, blocks=blocks)

# Lambda handler
slack_handler = SlackRequestHandler(app=app)

def handler(event, context):
    response = slack_handler.handle(event, context)

    return {
        'statusCode': response.get('statusCode', 200),
        'body': json.dumps(response.get('body', {})),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
