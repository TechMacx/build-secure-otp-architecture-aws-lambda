import boto3
import json
import base64
import os
import random
from datetime import datetime, timedelta
from botocore.exceptions import BotoCoreError, ClientError

# Initialize AWS services
kms_client = boto3.client('kms')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
ses_client = boto3.client('ses')

# Environment variables
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE', 'otp_main')
KMS_KEY_ID = os.getenv('KMS_KEY_ID')
SES_FROM_EMAIL = os.getenv('SES_FROM_EMAIL')

# Initialize DynamoDB Table
table = dynamodb.Table(DYNAMODB_TABLE)

def generate_otp():
    return str(random.randint(100000, 999999))

def encrypt_otp(otp):
    try:
        encrypted = kms_client.encrypt(
            KeyId=KMS_KEY_ID,
            Plaintext=otp.encode('utf-8')
        )
        return base64.b64encode(encrypted['CiphertextBlob']).decode('utf-8')
    except (BotoCoreError, ClientError) as e:
        print(f"KMS encryption error: {e}")
        return None

def store_otp_in_dynamodb(user_id, encrypted_otp):
    try:
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
        print(f"Storing OTP for user_id: {user_id}")  # Debugging
        table.put_item(
            Item={
                'user_id': user_id,
                'otp_code': encrypted_otp,
                'creation_timestamp': datetime.utcnow().isoformat(),
                'expiration_timestamp': expiration_time.isoformat(),
                'attempts': 3
            }
        )
        return True
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return False

def send_sms(phone_number, message):
    try:
        sns_client.publish(
            PhoneNumber=phone_number,
            Message=message
        )
        return True
    except ClientError as e:
        print(f"SNS error: {e}")
        return False

def send_email(email, subject, message):
    try:
        ses_client.send_email(
            Source=SES_FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': message}}
            }
        )
        return True
    except ClientError as e:
        print(f"SES error: {e}")
        return False

def lambda_handler(event, context):
    try:
        # Ensure event['body'] exists and is a string
        body = event['body'] if isinstance(event['body'], dict) else json.loads(event['body'])
        user_id = body.get('user_id')
        delivery_method = body.get('method')
        recipient = body.get('recipient')

        # Generate and encrypt OTP
        otp = generate_otp()
        print(f"Generated OTP (before encryption): {otp}")  # Debugging
        encrypted_otp = encrypt_otp(otp)
        if not encrypted_otp:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Failed to encrypt OTP'})}

        # Store OTP in DynamoDB
        if not store_otp_in_dynamodb(user_id, encrypted_otp):
            return {'statusCode': 500, 'body': json.dumps({'message': 'Failed to store OTP'})}

        message = f"Your OTP is: {otp}"

        # Send OTP via selected method
        if delivery_method == 'sms':
            success = send_sms(recipient, message)
        elif delivery_method == 'email':
            success = send_email(recipient, "Your OTP Code", message)
        else:
            return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid delivery method'})}

        if success:
            return {'statusCode': 200, 'body': json.dumps({'message': 'OTP sent successfully'})}
        else:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Failed to send OTP'})}

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'message': 'Internal server error'})}