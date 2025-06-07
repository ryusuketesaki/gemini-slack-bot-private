# Gemini Slack Bot

SlackでGemini APIを利用してチャットボットを実現するアプリケーションです。

## 機能

- Slackでのメンションに対してGemini APIを使用して応答
- API使用量の制限機能（DynamoDBで管理）
- CloudFrontを使用したエンドポイントの提供

## 技術スタック

- AWS CDK (TypeScript)
- AWS Lambda (Python)
- Amazon DynamoDB
- Amazon CloudFront
- Slack Bolt for Python
- Google Gemini API

## 開発環境のセットアップ

### 前提条件

- Node.js (v20.0.0以上)
- Python 3.9以上
- AWS CLI
- AWS CDK CLI

### 環境構築

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/gemini-slack-bot-private.git
cd gemini-slack-bot-private
```

2. Python依存関係のインストール
```bash
pip install -r requirements.txt
```

3. CDKの依存関係のインストール
```bash
cd cdk
npm install
cd ..
```

### 認証情報の設定

#### AWS認証情報

1. AWS CLIのインストール（まだの場合）
```bash
brew install awscli
```

2. AWS認証情報の設定
```bash
aws configure
```
以下の情報を入力：
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (例: ap-northeast-1)
- Default output format (json)

3. 認証状態の確認
```bash
aws sts get-caller-identity
```

#### アプリケーション認証情報

1. `.env`ファイルの作成
```bash
cp .env.example .env
```

2. 以下の環境変数を設定
```bash
# Slack API認証情報
SLAoCK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token

# Gemini API認証情報
GEMINI_API_KEY=your-api-key
```

### デプロイ

1. CDKのブートストラップ（初回のみ）
```bash
cd cdk
cdk bootstrap --profile [プロファイル名]
```

2. 変更内容の確認（dry-run）
```bash
cdk diff --profile [プロファイル名]
```
このコマンドでは実際のデプロイは行わず、以下の内容を確認できます：
- 作成される新しいリソース
- 更新されるリソースとその変更内容
- 削除されるリソース
- 推定コストの変更

3. デプロイの実行
```bash
cdk deploy --profile [プロファイル名]
```

デプロイ完了後、CloudFrontのURLが出力されます。このURLをSlackアプリの設定で使用してください。

> **ベストプラクティス**
> - 本番環境へのデプロイ前には必ず`cdk diff`で変更内容を確認する
> - 意図しない変更がないことを確認してからデプロイを実行する
> - 変更が大きい場合は、チームでレビューを行う

## セキュリティのベストプラクティス

### AWS認証情報の管理

1. アクセスキーのローテーション
   - 定期的にアクセスキーを更新
   - 古いキーは適切に無効化

2. 最小権限の原則
   - デプロイに必要な最小限の権限のみを持つIAMユーザーを作成
   - 必要なサービスのみにアクセス可能な権限を付与

3. 環境変数の管理
   - `.env`ファイルは決してGitにコミットしない
   - 本番環境では環境変数をAWS Systems ManagerやSecrets Managerで管理

### CI/CD環境での認証情報管理

GitHub Actionsを使用する場合：
1. リポジトリのSecretsとして認証情報を設定
2. OIDC認証の使用を推奨

## 開発フロー

1. 機能開発は新しいブランチを作成して実施
```bash
git checkout -b feature/your-feature-name
```

2. コードの変更とテスト
3. プルリクエストの作成
4. レビュー後にマージ

## トラブルシューティング

### APIエンドポイントのテスト

CloudFrontエンドポイントの動作確認には以下のcurlコマンドを使用できます：

1. 基本的なテストリクエスト：
```bash
#!/bin/bash

# 設定変数
CLOUDFRONT_DOMAIN="d1kabsc01ekmc1.cloudfront.net"  # あなたのCloudFrontドメイン
SLACK_SIGNING_SECRET="your-slack-signing-secret"   # Slackアプリの署名シークレット
BOT_USER_ID="U0123456789"                         # ボットのユーザーID
TEST_MESSAGE="テストメッセージ"                    # テストで送信するメッセージ

# タイムスタンプの設定
TIMESTAMP=$(date +%s)

# リクエストボディの設定
SLACK_REQUEST_BODY=$(cat << EOF
{
  "type": "event_callback",
  "event": {
    "type": "app_mention",
    "user": "U0123456789",
    "text": "<@${BOT_USER_ID}> ${TEST_MESSAGE}",
    "ts": "${TIMESTAMP}.123456"
  }
}
EOF
)

# 署名の生成
SLACK_SIGNING_STRING="v0:${TIMESTAMP}:${SLACK_REQUEST_BODY}"
SLACK_SIGNATURE=$(echo -n "$SLACK_SIGNING_STRING" | openssl sha256 -hmac "${SLACK_SIGNING_SECRET}" -hex | sed 's/^.* //')

# リクエストの実行
curl -v -X POST https://${CLOUDFRONT_DOMAIN} \
  -H "Content-Type: application/json" \
  -H "X-Slack-Request-Timestamp: ${TIMESTAMP}" \
  -H "X-Slack-Signature: v0=${SLACK_SIGNATURE}" \
  -d "${SLACK_REQUEST_BODY}"
```

2. デバッグ用の簡易テスト（署名検証なし）：
```bash
#!/bin/bash

# 設定変数
CLOUDFRONT_DOMAIN="xxx.cloudfront.net"  # あなたのCloudFrontドメイン
BOT_USER_ID="U0123456789"                         # ボットのユーザーID
TEST_MESSAGE="テストメッセージ"                    # テストで送信するメッセージ

# タイムスタンプの設定
TIMESTAMP=$(date +%s)

# リクエストの実行
curl -v -X POST https://${CLOUDFRONT_DOMAIN} \
  -H "Content-Type: application/json" \
  -H "X-Slack-Request-Timestamp: ${TIMESTAMP}" \
  -H "X-Slack-Signature: v0=dummy" \
  -d "{
    \"type\": \"event_callback\",
    \"event\": {
      \"type\": \"app_mention\",
      \"user\": \"U0123456789\",
      \"text\": \"<@${BOT_USER_ID}> ${TEST_MESSAGE}\",
      \"ts\": \"${TIMESTAMP}.123456\"
    }
  }"
```

使い方：
1. スクリプトとして保存する場合：
   ```bash
   # テストスクリプトを作成
   vim test-slack-bot.sh

   # 実行権限を付与
   chmod +x test-slack-bot.sh

   # 実行
   ./test-slack-bot.sh
   ```

2. 変数の設定：
   - `CLOUDFRONT_DOMAIN`: あなたのCloudFrontドメイン
   - `SLACK_SIGNING_SECRET`: Slackアプリの署名シークレット（本格的なテストの場合のみ）
   - `BOT_USER_ID`: ボットのユーザーID
   - `TEST_MESSAGE`: テストで送信するメッセージ

注意点：
- 簡易テストは403エラーが返されるのが正常な動作です（署名検証に失敗するため）
- 本格的なテストを行う場合は、必ず正しい`SLACK_SIGNING_SECRET`を設定してください
- テストの前に、CloudFrontとLambda関数が正しくデプロイされていることを確認してください

### よくある問題

1. AWS認証エラー
   - `aws configure`で認証情報が正しく設定されているか確認
   - IAMユーザーに必要な権限があるか確認

2. デプロイエラー
   - CDKのブートストラップが実行されているか確認
   - リージョンの設定が正しいか確認

3. Slack連携エラー
   - トークンが正しく設定されているか確認
   - アプリのスコープが適切か確認
   - Slack署名の検証が正しく機能しているか確認（curlテストで確認可能）
s
