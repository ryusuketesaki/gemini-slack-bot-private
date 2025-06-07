#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { GeminiSlackBotStack } from '../lib/gemini-slack-bot-stack';

const app = new cdk.App();
new GeminiSlackBotStack(app, 'GeminiSlackBotStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
