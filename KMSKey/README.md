

# Solution: Use a Different Key or Avoid Direct Encryption Calls
**You have two options:**

## ***Option 1:*** Use Customer managed keys for Otp service  **(Recommended)** || AWS Managed Key (aws/lambda) (`Option 1.2: wouldn't work`)
Instead of using the DynamoDB managed key **`(aws/dynamodb)`** or an AWS-managed key for Lambda **`(aws/lambda)`**, use a **`Customer managed keys`** by AWS. This key is already configured to allow Lambda & DynamoDB to perform encryption/decryption operations.

* Modify your Lambda IAM policy to allow **`kms:Encrypt`** and **`kms:Decrypt`** on the Lambda and for DynamoDB table follow steps from AWS Console.

### ***1.1: Updated IAM Role Policy for Lambda Functions (generate-otp & verify-otp).***
```yml
{
"Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
            "kms:Encrypt",
            "kms:Decrypt"
        ],
        "Resource": "arn:aws:kms:<AWS_REGION>:<AWS_ACCOUNT_ID>:key/<KMS_KEY_ID>"
        }
    ]
}
```
* ***Update your Lambda environment variable:***
Set `KMS_KEY_ID` to `CUSTOMAR_MANAGED_KEY_ID` instead of lambda or DynamoDB key, just like below example.

    * Set `KMS_KEY_ID` to `aws/lambda` instead of your DynamoDB key.

### ***1.2: Updated KMS Key Policy***
This policy allows both Lambda and DynamoDB to use the KMS key.

```json
{
  "Version": "2012-10-17",
  "Id": "key-policy",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<AWS_ACCOUNT_ID>:root"
      },
      "Action": "kms:*",
      "Resource": "arn:aws:kms:<AWS_REGION>:<AWS_ACCOUNT_ID>:key/<KMS_KEY_ID>"
    },
    {
      "Sid": "Allow DynamoDB to Use KMS",
      "Effect": "Allow",
      "Principal": {
        "Service": "dynamodb.amazonaws.com"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "arn:aws:kms:<AWS_REGION>:<AWS_ACCOUNT_ID>:key/<KMS_KEY_ID>",
      "Condition": {
        "StringEquals": {
          "kms:CallerAccount": "<AWS_ACCOUNT_ID>"
        },
        "StringLike": {
          "kms:ViaService": "dynamodb.<AWS_REGION>.amazonaws.com"
        }
      }
    },
    {
      "Sid": "Allow Lambda Function to Use KMS",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<AWS_ACCOUNT_ID>:role/service-role/deliver-otp-lambda-role-1agnqskx"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "arn:aws:kms:<AWS_REGION>:<AWS_ACCOUNT_ID>:key/<KMS_KEY_ID>"
    }
  ]
}
```

Working Sample JSON file for KMS policy: 
```JSON
{
	"Version": "2012-10-17",
	"Id": "key-policy",
	"Statement": [
		{
			"Sid": "Enable IAM User Permissions",
			"Effect": "Allow",
			"Principal": {
				"AWS": "arn:aws:iam::533267268334:root"
			},
			"Action": "kms:*",
			"Resource": "arn:aws:kms:ap-south-1:533267268334:key/0cf5bb9c-8dee-41d4-99ca-63434a381758"
		},
		{
			"Sid": "Allow DynamoDB to Use KMS",
			"Effect": "Allow",
			"Principal": {
				"Service": "dynamodb.amazonaws.com"
			},
			"Action": [
				"kms:Encrypt",
				"kms:Decrypt",
				"kms:ReEncrypt*",
				"kms:GenerateDataKey*",
				"kms:DescribeKey"
			],
			"Resource": "arn:aws:kms:ap-south-1:533267268334:key/0cf5bb9c-8dee-41d4-99ca-63434a381758",
			"Condition": {
				"StringEquals": {
					"kms:CallerAccount": "533267268334"
				},
				"StringLike": {
					"kms:ViaService": "dynamodb.ap-south-1.amazonaws.com"
				}
			}
		},
		{
			"Sid": "Allow Lambda Function to Use KMS",
			"Effect": "Allow",
			"Principal": {
				"AWS": "arn:aws:iam::533267268334:role/service-role/deliver-otp-lambda-role-1agnqskx"
			},
			"Action": [
				"kms:Encrypt",
				"kms:Decrypt",
				"kms:GenerateDataKey"
			],
			"Resource": "arn:aws:kms:ap-south-1:533267268334:key/0cf5bb9c-8dee-41d4-99ca-63434a381758"
		}
	]
}
```

### ***1.3: Step to updated DynamoDB Encryption with KMS Key***

1. Open the otp_main table.
2. Go to **`Additional settings`** tab.
3. Click on the **`Encryption`** tab.
4. Click on the  **`Manage encryption`** 
5. Choose the option **`Stored in your account, and owned and managed by you`** attribute. Select the KMS key (ARN).
6. Click **Save Changes**.

## ***Option 2:*** Remove KMS Encryption (If Not Mandatory)
If encryption is not strictly required, store the OTP in plain text in DynamoDB. DynamoDB provides built-in encryption at rest, and using KMS for OTP storage might be redundant.

***Modify the Code:***

* Remove **`encrypt_otp()`** function calls.
* Store **`otp`** directly in DynamoDB instead of **`encrypted_otp`**.