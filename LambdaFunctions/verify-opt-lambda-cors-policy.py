import boto3
import json
import base64
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError, ClientError

# Initialize AWS Clients
dynamodb = boto3.resource("dynamodb")
kms_client = boto3.client("kms")

# Environment Variables
table_name = os.getenv("DYNAMODB_TABLE", "otp_main")
kms_key_id = os.getenv("KMS_KEY_ID")

# Initialize DynamoDB Table
table = dynamodb.Table(table_name)

def decrypt_otp(encrypted_otp):
    """Decrypts the OTP using AWS KMS."""
    try:
        decrypted = kms_client.decrypt(CiphertextBlob=base64.b64decode(encrypted_otp))
        decrypted_otp = decrypted["Plaintext"].decode("utf-8")
        print(f"Decrypted OTP: {decrypted_otp}")  # Debug log
        return decrypted_otp
    except (BotoCoreError, ClientError) as e:
        print(f"KMS Decryption Error: {e}")
        return None

def verify_otp(user_id, otp_entered):
    """Verifies the OTP entered by the user."""
    try:
        print(f"Fetching OTP for user_id: {user_id}")
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
            Limit=1  # Fetch the latest OTP
        )
        print(f"DynamoDB Response: {response}")  # Debug log

        if "Items" not in response or not response["Items"]:
            #return {"statusCode": 400, "body": json.dumps({"message": "OTP not found or expired"})}
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"message": "OTP not found or expired"})
            }

        item = response["Items"][0]
        decrypted_otp = decrypt_otp(item["otp_code"])

        if not decrypted_otp:
            # return {"statusCode": 500, "body": json.dumps({"message": "Failed to decrypt OTP"})}
            return {
                'statusCode': 500,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"message": "Failed to decrypt OTP"})
            }
        if decrypted_otp != otp_entered:
            remaining_attempts = int(item.get("attempts", 3)) - 1
            table.update_item(
                Key={"user_id": user_id, "creation_timestamp": item["creation_timestamp"]},
                UpdateExpression="SET attempts = :attempts",
                ExpressionAttributeValues={":attempts": remaining_attempts}
            )
            if remaining_attempts <= 0:
                print(f"Deleting expired OTP for user_id: {user_id} and creation_timestamp: {item.get('creation_timestamp')}")
                table.delete_item(
                    Key={
                        "user_id": user_id,
                        "creation_timestamp": item["creation_timestamp"]  # Ensure sort key is included
                    }
                )
                # return {"statusCode": 400, "body": json.dumps({"message": "OTP expired or max attempts reached"})}
                return {
                    'statusCode': 400,
                    'headers': {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST",
                        "Access-Control-Allow-Headers": "Content-Type",
                    },
                    "body": json.dumps({"message": "OTP expired or max attempts reached"})
                }
            # return {"statusCode": 400, "body": json.dumps({"message": "Invalid OTP"})}
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"message": "Invalid OTP"})
            }
        # Check expiration time
        expiration_time = datetime.fromisoformat(item["expiration_timestamp"])
        if datetime.utcnow() > expiration_time:
            print(f"Deleting expired OTP for user_id: {user_id} and creation_timestamp: {item.get('creation_timestamp')}")
            table.delete_item(
                Key={
                    "user_id": user_id,
                    "creation_timestamp": item["creation_timestamp"]  # Ensure sort key is included
                }
            )
            # return {"statusCode": 400, "body": json.dumps({"message": "OTP expired"})}
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"message": "OTP expired"})
            }
        # Delete OTP after successful verification
        print(f"Deleting successfully verified OTP for user_id: {user_id} and creation_timestamp: {item.get('creation_timestamp')}")
        table.delete_item(
            Key={
                "user_id": user_id,
                "creation_timestamp": item["creation_timestamp"]  # Ensure sort key is included
            }
        )
        # return {"statusCode": 200, "body": json.dumps({"message": "OTP verified successfully"})}
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"message": "OTP verified successfully"})
        }

    except Exception as e:
        print(f"Error: {e}")
        # return {"statusCode": 500, "body": json.dumps({"message": "Internal server error"})}
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"message": "Internal server error"})
        }        

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        user_id = body.get("user_id")
        otp_code = body.get("otp_code")

        if not user_id or not otp_code:
            # return {"statusCode": 400, "body": json.dumps({"message": "Missing user_id or otp_code"})}
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"message": "Missing user_id or otp_code"})
            }            

        return verify_otp(user_id, otp_code)
    except Exception as e:
        print(f"Lambda Handler Error: {e}")
        # return {"statusCode": 500, "body": json.dumps({"message": "Internal server error"})}
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"message": "Internal server error"})
        }        
