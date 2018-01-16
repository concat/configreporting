import boto3
import os
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
    s3bucketobjkey = event['s3bucketobjkey']
    
    # create raw email
    msg = MIMEMultipart()
    msg['Subject'] = 'AWSConfig Compliance Report'
    msg['From'] = mySender
    msg['To'] = myRecipients

    part = MIMEText('Attached are AWSConfig Compliance reports')
    msg.attach(part)

    response = s3_client.get_object(Bucket=myBucket, Key=s3bucketobjkey)
    emailcontent = response['Body'].read()

    part = MIMEApplication(emailcontent)
    part.add_header('Content-Disposition', 'attachment', filename='ComplianceReport.pdf')
    msg.attach(part)

    
    ses.send_raw_email(RawMessage={
                       'Data': msg.as_string(),
                   }, 
                   Source=msg['From'],
                   Destinations=[msg['To']]
                   )