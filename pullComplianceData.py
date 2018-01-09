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
    key =  's3compliance/' + accountId + '/resourcecompliance.json'       
    object = s3res.Object(bucketname, key)
    object.put(Body=json.dumps(compliance_output))
    
    non_compliant_output = []
    for resourceid in non_compliant_resources:
        response = configsess.get_compliance_details_by_resource(ResourceType='AWS::S3::Bucket',ResourceId=resourceid)
        for ruleresult in response['EvaluationResults']:
            rule_eval_output = { 'AccountId': accountId, 'ResourceId': resourceid }
            if ruleresult['ComplianceType'] == 'NON_COMPLIANT':
                rule_eval_output['ConfigRuleName'] = ruleresult['EvaluationResultIdentifier']['EvaluationResultQualifier']['ConfigRuleName']
                if 'Annotation' in ruleresult:
                    rule_eval_output['Annotation'] = ruleresult['Annotation']
                else:
                    rule_eval_output['Annotation'] = "No annotations for this rule are available"
                rule_eval_output['ConfigRuleInvokedTime'] = str(ruleresult['ConfigRuleInvokedTime'])
                non_compliant_output.append(rule_eval_output)
        logger.info("Non-Compliant Resource by Rules Violated: " + json.dumps(non_compliant_output))
    key =  's3compliance/' + accountId + '/noncompliantresourcedetails.json'    
    object = s3res.Object(bucketname, key)
    object.put(Body=json.dumps(non_compliant_output))
    
    return (compliance_output, non_compliant_output)


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    bucketname = os.environ['reporting_input_bucket']
    managed_accounts = os.environ['managed_accounts'].split()
    assume_role_arn_template = os.environ['assume_role_arn_template']
    # Get main account and pull its data first
    callerInfo = sts.get_caller_identity()
    accountId = callerInfo['Account']
    consolidated_resource_compliance_data = []
    consolidated_non_compliant_detail_data = []
    this_account_compliance_data, this_account_non_compliant_detail_data = get_compliance_data_by_account(accountId, bucketname, logger, "none")
    consolidated_resource_compliance_data.extend(this_account_compliance_data)
    consolidated_non_compliant_detail_data.extend(this_account_non_compliant_detail_data)    
    # Then pull data for each managed account
    for managed_account in managed_accounts:
        assume_role_arn = assume_role_arn_template % (managed_account)
        this_account_compliance_data, this_account_non_compliant_detail_data = get_compliance_data_by_account(managed_account, bucketname, logger, assume_role_arn)
        consolidated_resource_compliance_data.extend(this_account_compliance_data)
        consolidated_non_compliant_detail_data.extend(this_account_non_compliant_detail_data)
        
    logger.info("Consolidated compliance data is : " + json.dumps(consolidated_resource_compliance_data))
    key =  's3compliance/resourcecompliance.json'       
    object = s3res.Object(bucketname, key)
    object.put(Body=json.dumps(consolidated_resource_compliance_data))
    
    logger.info("Consolidated non_compliant detail data is : " + json.dumps(consolidated_non_compliant_detail_data))
    key =  's3compliance/noncompliantresourcesdetails.json'    
    object = s3res.Object(bucketname, key)
    object.put(Body=json.dumps(consolidated_non_compliant_detail_data))