'use strict';
const AWS = require('aws-sdk');
const stepfunctions = new AWS.StepFunctions();

exports.handler = (event, context, callback) => {
  const stateMachineArn = process.env.STATEMACHINE_ARN;
  const params = {
    stateMachineArn
  }

  return stepfunctions.startExecution(params).promise().then(() => {
    callback(null, `Your statemachine ${stateMachineArn} executed successfully`);
  }).catch(error => {
    callback(error.message);
  });
};