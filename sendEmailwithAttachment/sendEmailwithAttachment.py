import boto3
import os
import logging
import json
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

ses = boto3.client('ses')
s3_client = boto3.client('s3')

myBucket = os.environ['reporting_input_bucket']
mySender = os.environ['sender']
myRecipients = os.environ['recipients']

def lambda_handler(event, context):
    # get filename from event
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    eventtype = type(event)

    
    # Allow for event to be either dict as returned by preceding function if not using Step Function branches
    # or a list if parallel branches are used as the preceding part of the flow.
    # Wrap an event dict in an array to support both possibilities.

    if eventtype is dict:
        myInput = [ event ]
        myInputType = 'dict'
    else:
        myInput = event
        myInputType = 'list'
        
    logger.info("Event data is of type " + myInputType + ": " + json.dumps(event))
    # create raw email
    msg = MIMEMultipart()
    msg['Subject'] = 'AWSConfig Compliance Report'
    msg['From'] = mySender
    msg['To'] = myRecipients

    part = MIMEText('Attached are AWSConfig Compliance reports')
    msg.attach(part)
    
    for fileinfo in myInput:
        filekey=fileinfo['s3bucketobjkey']
        response = s3_client.get_object(Bucket=myBucket, Key=filekey)
        emailcontent = response['Body'].read()

        part = MIMEApplication(emailcontent)
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filekey))
        msg.attach(part)
