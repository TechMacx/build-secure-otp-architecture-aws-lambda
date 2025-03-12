import boto3
import json
import base64
import os
import random
from datetime import datetime, timedelta
from botocore.exceptions import BotoCoreError, ClientError
import time

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

# Common headers for all responses
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
    "Access-Control-Allow-Headers": "Content-Type",
}

def create_response(status_code, message):
    """Helper function to create consistent response objects"""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps({'message': message}, ensure_ascii=False)
        #'body': message
    }

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
        current_time = datetime.utcnow()
        expiration_time = current_time + timedelta(minutes=10)
        
        # Convert to epoch time for TTL
        ttl_timestamp = int(expiration_time.timestamp())
        
        print(f"Storing OTP for user_id: {user_id}")  # Debugging
        table.put_item(
            Item={
                'user_id': user_id,
                'otp_code': encrypted_otp,
                'creation_timestamp': current_time.isoformat(),
                'expiration_timestamp': expiration_time.isoformat(),  # Keep for backward compatibility
                'ttl_timestamp': ttl_timestamp,  # DynamoDB TTL field (epoch time in seconds)
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
        # Check if event contains a body
        if 'body' not in event:
            print("Error: 'body' not found in event: ", event)
            return create_response(400, 'Missing request body')
        
        # Handle empty body
        if event['body'] is None:
            print("Error: 'body' is None")
            return create_response(400, 'Empty request body')
            
        # Parse body based on its type
        try:
            body = event['body'] if isinstance(event['body'], dict) else json.loads(event['body'])
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON body: {e}, Body: {event['body']}")
            return create_response(400, 'Invalid JSON in request body')
        
        # Validate required fields
        if not all(key in body for key in ['user_id', 'method', 'recipient']):
            missing_fields = [field for field in ['user_id', 'method', 'recipient'] if field not in body]
            print(f"Missing required fields: {missing_fields}")
            return create_response(400, f"Missing required fields: {', '.join(missing_fields)}")
        
        user_id = body.get('user_id')
        delivery_method = body.get('method')
        recipient = body.get('recipient')

        # Generate and encrypt OTP
        otp = generate_otp()
        print(f"Generated OTP (before encryption): {otp}")  # Debugging
        encrypted_otp = encrypt_otp(otp)
        if not encrypted_otp:
            return create_response(500, 'Failed to encrypt OTP')

        # Store OTP in DynamoDB
        if not store_otp_in_dynamodb(user_id, encrypted_otp):
            return create_response(500, 'Failed to store OTP')

        message = f"Your OTP is: {otp}"

        # Send OTP via selected method
        if delivery_method == 'sms':
            success = send_sms(recipient, message)
        elif delivery_method == 'email':
            success = send_email(recipient, "Your OTP Code", message)
        else:
            return create_response(400, f'Invalid delivery method: {delivery_method}')

        if success:
            return create_response(200, 'OTP sent successfully')
        else:
            return create_response(500, 'Failed to send OTP')

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return create_response(500, 'Internal server error')