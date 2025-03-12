#!/bin/bash

# Load configuration
CONFIG_FILE="./config.ini"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "Error: Configuration file $CONFIG_FILE not found!"
    exit 1
fi

# Set AWS region and table name
AWS_REGION=${AWS_REGION:-"us-east-1"}  # Default to us-east-1 if not set
TABLE_NAME=${TABLE_NAME:-"otp_main"}
PROFILE=${1:-"default"}  # Use the first argument as profile, default if not provided

# Create DynamoDB table
aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=creation_timestamp,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=creation_timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region "$AWS_REGION" \
    --profile "$PROFILE"

# # Enable TTL on expiration_timestamp
# aws dynamodb update-time-to-live \
#     --table-name "$TABLE_NAME" \
#     --time-to-live-specification Enabled=true,AttributeName=expiration_timestamp \
#     --region "$AWS_REGION" \
#     --profile "$PROFILE"

# Enable TTL on ttl_timestamp (numeric epoch time field)
aws dynamodb update-time-to-live \
    --table-name "$TABLE_NAME" \
    --time-to-live-specification Enabled=true,AttributeName=ttl_timestamp \
    --region "$AWS_REGION" \
    --profile "$PROFILE"

# Output success message
echo "DynamoDB table '$TABLE_NAME' created successfully with TTL enabled on 'ttl_timestamp'"
