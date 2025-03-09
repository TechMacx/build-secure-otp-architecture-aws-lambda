#!/bin/bash

AWS_REGION="ap-south-1"  # Change to your AWS region
AWS_ACCOUNT_ID="XXXXXXXXXXXX"  # Replace with your AWS account ID
DYNAMODB_TABLE_NAME="otp_main"  # Your DynamoDB table name
LAMBDA_ROLE="arn:aws:iam::$AWS_ACCOUNT_ID:role/service-role/deliver-otp-lambda-role-1agnqskx"
AWS_PROFILE=${1:-"default"}  # Allow passing profile as argument, default to "default"

# Step 1: Create a Customer Managed Key in AWS KMS
KMS_KEY_ID=$(aws kms create-key --query 'KeyMetadata.KeyId' --output text --profile "$AWS_PROFILE")
KMS_KEY_ARN="arn:aws:kms:$AWS_REGION:$AWS_ACCOUNT_ID:key/$KMS_KEY_ID"
echo "Created KMS Key: $KMS_KEY_ARN"

# Step 2: Attach a Key Policy to Allow Lambda & DynamoDB
cat > kms-policy.json <<EOL
{
  "Version": "2012-10-17",
  "Id": "key-policy",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::$AWS_ACCOUNT_ID:root" },
      "Action": "kms:*",
      "Resource": "$KMS_KEY_ARN"
    },
    {
      "Sid": "Allow DynamoDB to Use KMS",
      "Effect": "Allow",
      "Principal": { "Service": "dynamodb.amazonaws.com" },
      "Action": ["kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey"],
      "Resource": "$KMS_KEY_ARN",
      "Condition": {
        "StringEquals": { "kms:CallerAccount": "$AWS_ACCOUNT_ID" },
        "StringLike": { "kms:ViaService": "dynamodb.$AWS_REGION.amazonaws.com" }
      }
    },
    {
      "Sid": "Allow Lambda Function to Use KMS",
      "Effect": "Allow",
      "Principal": { "AWS": "$LAMBDA_ROLE" },
      "Action": ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey"],
      "Resource": "$KMS_KEY_ARN"
    }
  ]
}
EOL

aws kms put-key-policy --key-id "$KMS_KEY_ID" --policy file://kms-policy.json --profile "$AWS_PROFILE"

echo "Updated KMS key policy for Lambda and DynamoDB access."

# Step 3: Attach IAM Policy to Lambda Role
cat > lambda-iam-policy.json <<EOL
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["kms:Encrypt", "kms:Decrypt"],
      "Resource": "$KMS_KEY_ARN"
    }
  ]
}
EOL

aws iam put-role-policy --role-name deliver-otp-lambda-role-1agnqskx --policy-name KMSLambdaPolicy --policy-document file://lambda-iam-policy.json --profile "$AWS_PROFILE"

echo "Updated IAM policy for Lambda."

# Step 4: Update DynamoDB Encryption to Use the New KMS Key
aws dynamodb update-table --table-name "$DYNAMODB_TABLE_NAME" --sse-specification "Enabled=true,SSEType=KMS,KMSMasterKeyArn=$KMS_KEY_ARN" --profile "$AWS_PROFILE"

echo "Updated DynamoDB encryption settings to use the new KMS key."

echo "Setup completed successfully!"
