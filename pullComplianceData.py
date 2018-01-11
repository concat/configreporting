import boto3
import logging
import json
import os


sts = boto3.client('sts')
config = boto3.client('config')
s3res = boto3.resource('s3')

def get_compliance_data_by_account(accountId, bucketname, logger, assume_role_arn):
    logger.info("AccountId is " + accountId)
    if assume_role_arn != "none":
        logger.info("AssumeRole ARN is " + assume_role_arn)
        roleSessionName="configrulecrossaccount" + accountId
        assumeroleresult = sts.assume_role(RoleArn=assume_role_arn,RoleSessionName=roleSessionName)
        configsess = boto3.client(
            'config',
            aws_access_key_id=assumeroleresult['Credentials']['AccessKeyId'],
            aws_secret_access_key=assumeroleresult['Credentials']['SecretAccessKey'],
            aws_session_token=assumeroleresult['Credentials']['SessionToken'])
    else:
        configsess = boto3.client('config')
    response = configsess.describe_compliance_by_resource(ResourceType='AWS::S3::Bucket')
    resource_ids = []
    compliance_output = {}
    logger.info("Response is" + json.dumps(response) + ".")
    for resource in response['ComplianceByResources']:
        resource_output = { 'BucketCompliance': resource['Compliance']['ComplianceType']}
        compliance_output[resource['ResourceId']] = resource_output
        resource_ids.append(resource['ResourceId'])
    
    logger.info("Compliance Output is " + json.dumps(compliance_output))
    
    detailed_resource_output = []
    for resourceid in resource_ids:
        response = configsess.get_compliance_details_by_resource(ResourceType='AWS::S3::Bucket',ResourceId=resourceid)
        for ruleresult in response['EvaluationResults']:
            rule_eval_output = { 'AccountId': accountId, 'ResourceType': 'S3 Bucket', 'BucketCompliance': compliance_output[resourceid]['BucketCompliance'], 'ResourceId': resourceid, 'RuleCompliance': ruleresult['ComplianceType'], 'ConfigRuleName': ruleresult['EvaluationResultIdentifier']['EvaluationResultQualifier']['ConfigRuleName'] }
            rule_eval_output['ConfigRuleInvokedTime'] = str(ruleresult['ConfigRuleInvokedTime'])            
            if ruleresult['ComplianceType'] == 'NON_COMPLIANT':
                if 'Annotation' in ruleresult:
                    rule_eval_output['Annotation'] = ruleresult['Annotation']
                else:
                    rule_eval_output['Annotation'] = "No annotations for this rule are available"
            detailed_resource_output.append(rule_eval_output)
    logger.info("Detailed Resource Rule Compliance is " + json.dumps(detailed_resource_output))
    
    return (detailed_resource_output)


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    bucketname = os.environ['reporting_input_bucket']
    managed_accounts = os.environ['managed_accounts'].split()
    assume_role_arn_template = os.environ['assume_role_arn_template']
    # Get main account and pull its data first
    callerInfo = sts.get_caller_identity()
    accountId = callerInfo['Account']
    consolidated_detail_data = []
    this_account_detail_data = get_compliance_data_by_account(accountId, bucketname, logger, "none")
    consolidated_detail_data.extend(this_account_detail_data)    
    # Then pull data for each managed account
    for managed_account in managed_accounts:
        assume_role_arn = assume_role_arn_template % (managed_account)
        this_account_detail_data = get_compliance_data_by_account(managed_account, bucketname, logger, assume_role_arn)
        consolidated_detail_data.extend(this_account_detail_data)
    
    logger.info("Consolidated detail data is : " + json.dumps(consolidated_detail_data))
    key =  's3compliance/resourcescompliancetorules.json'    
    object = s3res.Object(bucketname, key)
    object.put(Body=json.dumps(consolidated_detail_data))