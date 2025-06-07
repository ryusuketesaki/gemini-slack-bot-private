import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class GeminiSlackBotStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // API使用量管理用のDynamoDBテーブル
    const apiUsageTable = new dynamodb.Table(this, 'GeminiApiUsage', {
      partitionKey: { name: 'date', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      timeToLiveAttribute: 'ttl',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Lambdaレイヤーの作成
    const dependenciesLayer = new lambda.LayerVersion(this, 'DependenciesLayer', {
      code: lambda.Code.fromAsset('../src/lambda_layer.zip'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_9],
      description: 'Dependencies for the bot function',
    });

    // Lambda関数
    const botFunction = new lambda.Function(this, 'BotFunction', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'app.handler',
      code: lambda.Code.fromAsset('../src'),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      layers: [dependenciesLayer],
      environment: {
        SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN!,
        SLACK_APP_TOKEN: process.env.SLACK_APP_TOKEN!,
        GEMINI_API_KEY: process.env.GEMINI_API_KEY!,
        GEMINI_DAILY_LIMIT: '1000',
      }
    });

    // Lambda関数にDynamoDBへのアクセス権限を付与
    apiUsageTable.grantReadWriteData(botFunction);

    // Lambda関数URL
    const functionUrl = botFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ['*'],
        allowedMethods: [lambda.HttpMethod.POST],
        allowedHeaders: ['content-type', 'x-slack-signature', 'x-slack-request-timestamp']
      }
    });

    // CloudFront
    const cloudfrontConfig = this.node.tryGetContext('cloudfront');
    const distribution = new cloudfront.Distribution(this, 'BotDistribution', {
      defaultBehavior: {
        origin: new origins.FunctionUrlOrigin(functionUrl),
        allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
        originRequestPolicy: new cloudfront.OriginRequestPolicy(this, 'SlackRequestPolicy', {
          headerBehavior: cloudfront.OriginRequestHeaderBehavior.allowList(
            'content-type',
            'x-slack-signature',
            'x-slack-request-timestamp'
          ),
          queryStringBehavior: cloudfront.OriginRequestQueryStringBehavior.none(),
          cookieBehavior: cloudfront.OriginRequestCookieBehavior.none(),
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
        responseHeadersPolicy: cloudfront.ResponseHeadersPolicy.CORS_ALLOW_ALL_ORIGINS
      },
      enabled: cloudfrontConfig.distribution.enabled,
      defaultRootObject: cloudfrontConfig.distribution.defaultRootObject,
      priceClass: cloudfront.PriceClass.PRICE_CLASS_100,
      httpVersion: cloudfrontConfig.distribution.httpVersion
    });

    // 出力
    new cdk.CfnOutput(this, 'EndpointUrl', {
      value: distribution.distributionDomainName,
      description: 'Endpoint URL for Slack',
    });
  }
}
