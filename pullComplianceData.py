import boto3
import logging
import json
import os
import datetime

sts = boto3.client('sts')
config = boto3.client('config')
s3res = boto3.resource('s3')

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    bucketname = os.environ['reporting_input_bucket']
    
    callerInfo = sts.get_caller_identity()
    accountId = callerInfo['Account']
    logger.info("AccountId is " + accountId)
    response = config.describe_compliance_by_resource(ResourceType='AWS::S3::Bucket')
    non_compliant_resources = []
    compliance_output = []
    logger.info("Response is" + json.dumps(response) + ".")
    for resource in response['ComplianceByResources']:
        resource_output = {}
        logger.info("Resource is " + json.dumps(resource))
        logger.info("ResourceId is " + resource['ResourceId'])
        resource_output['AccountId'] = accountId
        resource_output['ResourceId'] = resource['ResourceId']
        resource_output['ComplianceStatus'] = resource['Compliance']['ComplianceType']
        compliance_output.append(resource_output)
        if resource['Compliance']['ComplianceType'] == "NON_COMPLIANT":
            non_compliant_resources.append(resource['ResourceId'])
    
    logger.info("Compliance Output is " + json.dumps(compliance_output))
    logger.info("Non-Compliant Resources is/are " + json.dumps(non_compliant_resources))
            
    object = s3res.Object(bucketname, 's3compliance/resourcecompliance.json')
    object.put(Body=json.dumps(compliance_output))
    
    non_compliant_output = []
    for resourceid in non_compliant_resources:
        #logger.info("datetime is: " + str(datetime.datetime.now()))
        response = config.get_compliance_details_by_resource(ResourceType='AWS::S3::Bucket',ResourceId=resourceid)
        for ruleresult in response['EvaluationResults']:
            rule_eval_output = { 'AccountId': accountId, 'ResourceId': resourceid }
            rule_eval_output['ConfigRuleName'] = ruleresult['EvaluationResultIdentifier']['EvaluationResultQualifier']['ConfigRuleName']
            rule_eval_output['Annotation'] = ruleresult['Annotation']
            rule_eval_output['ConfigRuleInvokedTime'] = str(ruleresult['ConfigRuleInvokedTime'])
            non_compliant_output.append(rule_eval_output)
        logger.info("Non-Compliant Resource by Rules Violated: " + json.dumps(non_compliant_output))
        
    object = s3res.Object(bucketname, 's3compliance/noncompliantresourcesdetails.json')
    object.put(Body=json.dumps(non_compliant_output))
