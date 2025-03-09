#!/bin/bash


if [ -z "$1" ]; then
  echo "Usage: $0 <AWS_PROFILE>"
  exit 1
fi

PROFILE=$1
AWS_REGION=$(aws configure get region --profile $PROFILE)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --query Account --output text)
ROLE_NAME="otp-service-lambda-role-xbo4r961"
KMS_KEY_ID="56733c0f-c7b9-4401-9cd7-9dd9ff1a92a4"
DYNAMODB_TABLE="otp_main"
LAMBDA_FUNCTIONS=("generate-otp-lambda" "verify-otp-lambda")

# Step 1: Create IAM Role
echo "Creating IAM Role: $ROLE_NAME"
aws iam create-role --profile $PROFILE --role-name $ROLE_NAME \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Step 2: Attach Required Policies

echo "Attaching DynamoDB Policy"
aws iam put-role-policy --profile $PROFILE --role-name $ROLE_NAME \
  --policy-name DynamoDBAccess \
  --policy-document "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Effect\": \"Allow\",
      \"Action\": [\"dynamodb:Query\", \"dynamodb:GetItem\", \"dynamodb:PutItem\", \"dynamodb:UpdateItem\", \"dynamodb:DeleteItem\"],
      \"Resource\": \"arn:aws:dynamodb:$AWS_REGION:$AWS_ACCOUNT_ID:table/$DYNAMODB_TABLE\"
    }]
  }"

echo "Attaching KMS Policy"
aws iam put-role-policy --profile $PROFILE --role-name $ROLE_NAME \
  --policy-name KMSAccess \
  --policy-document "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Effect\": \"Allow\",
      \"Action\": [\"kms:Encrypt\", \"kms:Decrypt\"],
      \"Resource\": \"arn:aws:kms:$AWS_REGION:$AWS_ACCOUNT_ID:key/$KMS_KEY_ID\"
    }]
  }"

echo "Attaching SNS Policy"
aws iam put-role-policy --profile $PROFILE --role-name $ROLE_NAME \
  --policy-name SNSAccess \
  --policy-document "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Effect\": \"Allow\",
      \"Action\": \"sns:Publish\",
      \"Resource\": \"*\"
    }]
  }"

echo "Attaching SES Policy"
aws iam put-role-policy --profile $PROFILE --role-name $ROLE_NAME \
  --policy-name SESAccess \
  --policy-document "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Effect\": \"Allow\",
      \"Action\": \"ses:SendEmail\",
      \"Resource\": \"*\"
    }]
  }"

echo "Attaching CloudWatch Policy"
aws iam put-role-policy --profile $PROFILE --role-name $ROLE_NAME \
  --policy-name CloudWatchAccess \
  --policy-document "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Effect\": \"Allow\",
      \"Action\": [\"logs:CreateLogGroup\", \"logs:CreateLogStream\", \"logs:PutLogEvents\"],
      \"Resource\": \"arn:aws:logs:$AWS_REGION:$AWS_ACCOUNT_ID:*\"
    }]
  }"

# Step 3: Attach IAM Role to Lambda Functions
echo "Attaching IAM Role to Lambda Functions"
for FUNCTION in "${LAMBDA_FUNCTIONS[@]}"; do
  echo "Updating function: $FUNCTION"
  aws lambda update-function-configuration --profile $PROFILE \
    --function-name $FUNCTION \
    --role arn:aws:iam::$AWS_ACCOUNT_ID:role/$ROLE_NAME
done

echo "✅ IAM Role setup completed successfully!"