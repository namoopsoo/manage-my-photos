#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { Ec2ControlApiStack } from '../lib/ec2_control_api_stack';

const app = new cdk.App();
new Ec2ControlApiStack(app, 'Ec2ControlApiStack');
