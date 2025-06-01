const AWS = require('aws-sdk');
const ec2 = new AWS.EC2({ region: process.env.REGION });

exports.handler = async (event) => {
  const instanceId = process.env.INSTANCE_ID;
  const action = event.resource.includes('start') ? 'start' : 'stop';

  await ec2[`${action}Instances`]({ InstanceIds: [instanceId] }).promise();

  return {
    statusCode: 200,
    body: JSON.stringify({ message: `EC2 instance ${action}ed.` })
  };
};
