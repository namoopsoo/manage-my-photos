

import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';

export class Ec2ControlApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Parameters
    const instanceId = 'i-xxxxxxxxxxxxxxxxx'; // Your EC2 instance ID
    const region = this.region;

    // Lambda Function to start/stop EC2 instance
    const ec2ControlFn = new lambda.Function(this, 'Ec2ControlFunction', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/ec2-control'),
      environment: {
        INSTANCE_ID: instanceId,
        REGION: region
      }
    });

    // IAM permissions for Lambda to control EC2
    ec2ControlFn.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'ec2:StartInstances',
        'ec2:StopInstances',
        'ec2:DescribeInstances'
      ],
      resources: ['*'] // optionally scope to specific instance ARN
    }));

    // API Gateway with /start and /stop endpoints
    const api = new apigateway.RestApi(this, 'Ec2ControlApi', {
      restApiName: 'EC2 Control Service',
      description: 'API to start and stop an EC2 instance.'
    });

    // Optional: simple API key auth
    const apiKey = api.addApiKey('ApiKey');
    const plan = api.addUsagePlan('UsagePlan', {
      name: 'EC2ControlUsagePlan',
      apiKey,
      throttle: {
        rateLimit: 5,
        burstLimit: 2
      }
    });
    plan.addApiStage({ stage: api.deploymentStage });

    const lambdaIntegration = new apigateway.LambdaIntegration(ec2ControlFn);

    const start = api.root.addResource('start');
    start.addMethod('POST', lambdaIntegration, {
      apiKeyRequired: true
    });

    const stop = api.root.addResource('stop');
    stop.addMethod('POST', lambdaIntegration, {
      apiKeyRequired: true
    });
  }
}
