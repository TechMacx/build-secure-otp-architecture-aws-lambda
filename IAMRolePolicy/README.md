## 1. Create IAM Role for Lambda Functions
Run the following AWS CLI command to create the role:
```bash
aws iam create-role --role-name otp-service-lambda-role-xbo4r961 \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'
```


## 2. Attach Required Policies
Now, attach the required permissions.

**2.1:** DynamoDB Policy (Allow OTP Read/Write) <br>
This grants access to otp_main DynamoDB table.
This creates an IAM role otp-service-lambda-role-xbo4r961 that Lambda can assume.
```shell
aws iam put-role-policy --profile ${PROFILE} --role-name otp-service-lambda-role-xbo4r961 \
  --policy-name DynamoDBAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "dynamodb:Query",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ],
        "Resource": "arn:aws:dynamodb:ap-south-1:${AWS_ACCOUNT_ID}:table/otp_main"
      }
    ]
  }'
```


**2.2:** KMS Policy (Allow OTP Encryption/Decryption) <br>
This policy allows Encrypting and Decrypting OTPs using KMS.
```shell
aws iam put-role-policy --profile $PROFILE --role-name otp-system-lambda-role-xbo4r961 \
  --policy-name KMSAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "kms:Encrypt",
          "kms:Decrypt"
        ],
        "Resource": "arn:aws:kms:ap-south-1:${AWS_ACCOUNT_ID}:key/56733c0f-c7b9-4401-9cd7-9dd9ff1a92a4"
      }
    ]
  }'
```


**2.3:** SNS Policy (Allow Sending OTP via SMS) <br>
This policy allows sending SMS via Amazon SNS.
```shell
aws iam put-role-policy --profile $PROFILE --role-name otp-system-lambda-role-xbo4r961 \
  --policy-name SNSAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "sns:Publish",
        "Resource": "*"
      }
    ]
  }'
```

**2.4:** SES Policy (Allow Sending OTP via Email) <br>
This policy allows sending OTP emails via SES.
```shell
aws iam put-role-policy --profile $PROFILE --role-name otp-system-lambda-role-xbo4r961 \
  --policy-name SESAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "ses:SendEmail",
        "Resource": "*"
      }
    ]
  }'
```

**2.5:** CloudWatch Logs Policy (For Debugging Lambda Logs) <br>
This policy allows Lambda to log errors and execution details to CloudWatch.

```shell
aws iam put-role-policy --profile $PROFILE --role-name otp-system-lambda-role-xbo4r961 \
  --policy-name CloudWatchAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource": "arn:aws:logs:${AWS_REGION}:*:*"
      }
    ]
  }'
```


**2.6:** AWSLambdaBasicExecutionRolePolicy (Default Lambda Role/Policy) <br>
This policy is created by default during creation of Lambda function to log errors and execution details to CloudWatch. __(Optional)__

```shell
aws iam put-role-policy --profile $PROFILE --role-name otp-system-lambda-role-xbo4r961 \
  --policy-name CloudWatchAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:ap-south-1:533267268334:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:ap-south-1:533267268334:log-group:/aws/lambda/deliver-otp-lambda:*"
            ]
        }
    ]
}'

## 3. Attach Role to Lambda Functions
Now, attach this IAM role to Deliver OTP and Verify OTP Lambda functions.

```bash
aws lambda update-function-configuration --function-name generate-otp-lambda \
  --role arn:aws:iam::<your-account-id>:role/otp-system-lambda-role-xbo4r961
```
```bash
aws lambda update-function-configuration --function-name verify-otp-lambda \
  --role arn:aws:iam::<your-account-id>:role/otp-system-lambda-role-xbo4r961
```

🎯 Final Summary <br>
✅ Created IAM Role **`OTPServiceLambdaRole`**
✅ Granted access to:
  * DynamoDB (Read/Write OTPs)
  * KMS (Encrypt/Decrypt OTPs)
  * SNS (Send SMS)
  * SES (Send Email)
  * CloudWatch Logs (Debugging) 

✅ Attached the role to both Lambda functions.<br>
🚀 Now your Lambda functions have the required permissions! Let me know if you need any changes.