# Steps to Create a DynamoDB Table for OTP Storage
Since your Lambda function references a DynamoDB table named otp_main, you need to create this table with the correct schema.


## Step 1: Open AWS DynamoDB Console
1. Go to the **AWS Management Console**.
2. Search for and open **DynamoDB**.
3. Click on **Create Table**.


## Step 2: Define Table Settings
1. Table Name: **`otp_main`**
2. Partition Key: **`user_id` (Type: String)**
3. Sort Key **(Optional but Recommended): `creation_timestamp`** (Type: String)
    * This helps to store multiple OTPs per user while allowing sorting by time.
4. **Set Read/Write Capacity:**
    * **Choose On-Demand (Recommended)** or manually set Provisioned Capacity if required.
5. Click **Create Table**.


## Step 3: Define Table Attributes
After the table is created, modify its attributes(Optional):

1. Add Additional Attributes:
    * **`otp_code`** (String) → Stores encrypted OTP.
    * **`expiration_timestamp`** (String) → Stores expiry time.
    * **`attempts`** (Number) → Tracks remaining OTP attempts.


## Step 4: Configure TTL (Time-to-Live)
1. Open the otp_main table.
2. Click on the **Time to Live (TTL)** tab.
3. Enable **TTL** on the **`expiration_timestamp`** attribute.
4. Click **Save**.
    * __This automatically deletes expired OTPs after their validity period__.


## Step 5: Add IAM Permissions for Lambda
Your Lambda function needs permissions to read and write to DynamoDB.

1. Open **IAM** → Go to **Roles**.
2. Find the IAM role associated with your **Lambda function**.
3. Attach the following policy:
```json
{
    "Effect": "Allow",
    "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:DeleteItem"
    ],
    "Resource": "arn:aws:dynamodb:<region>:<account-id>:table/otp_main"
}
```
4. Click Save Changes.


## Step 6: Test with Sample Data
Use AWS CLI or the DynamoDB console to insert sample OTP data:

```bash
aws dynamodb put-item --table-name otp_main --item '{
  "user_id": {"S": "user123"},
  "otp_code": {"S": "encrypted_otp_string"},
  "creation_timestamp": {"S": "2025-03-07T10:00:00Z"},
  "expiration_timestamp": {"S": "2025-03-07T10:10:00Z"},
  "attempts": {"N": "3"}
}'
```
This confirms that your table structure works correctly.

__Final Check__ 
* ✅ Table otp_main created with necessary attributes
* ✅ TTL enabled for automatic deletion
* ✅ Lambda has correct IAM permissions
* ✅ DynamoDB table ready for OTP storage 🚀



# How to Add Attributes in DynamoDB Table (`otp_main`)

Since DynamoDB is a NoSQL database, you don't predefine attributes like in relational databases. Instead, you store items dynamically with attributes included in your **`put_item`** request.

However, to ensure attributes exist consistently, follow these steps:

## Option 1: Add Attributes via AWS Console
1. Go to AWS Management Console → Open DynamoDB.
2. Click on Tables → Select your table otp_main.
3. Go to the Items tab → Click Create Item.
4. Add the required attributes:
    user_id → String (Partition Key)
    otp_code → String
    creation_timestamp → String
    expiration_timestamp → String
    attempts → Number
5. Click Save.
This will create a sample record, and DynamoDB will recognize these attributes.

## Option 2: Add Attributes Using AWS CLI
Run the following command to add an entry with all required attributes:

```bash
aws dynamodb put-item --table-name otp_main --item '{
  "user_id": {"S": "user123"},
  "otp_code": {"S": "encrypted_otp_string"},
  "creation_timestamp": {"S": "2025-03-07T10:00:00Z"},
  "expiration_timestamp": {"S": "2025-03-07T10:10:00Z"},
  "attempts": {"N": "3"}
}'
```
This will insert a sample OTP record with all attributes.

## Option 3: Define Attributes in Lambda Function (Already Done)
Your Deliver OTP Lambda already defines these attributes when inserting an OTP:

```python
def store_otp_in_dynamodb(user_id, encrypted_otp):
    try:
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
        print(f"Storing OTP for user_id: {user_id}")  # Debugging
        table.put_item(
            Item={
                'user_id': user_id, # Partition Key
                'otp_code': encrypted_otp, # Encrypted OTP
                'creation_timestamp': datetime.utcnow().isoformat(), # Creation time
                'expiration_timestamp': expiration_time.isoformat(), # Expiry time
                'attempts': 3 # Remaining attempts
            }
        )
        return True
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return False
```
__No need to manually define attributes because they will be created dynamically 
when an OTP is inserted. make sure `dynamodb:PutItem` is added in the lambda role__

✅ **Final Confirmation**
* No schema definition needed in NoSQL.
* Attributes get created dynamically when the first item is inserted.
* Use AWS Console, CLI, or Lambda function to check.
* Let me know if you need further clarifications! 🚀


## Shell Script to Create DynamoDB table.
```bash
#!/bin/bash

# Set AWS region and table name
AWS_REGION="us-east-1"  # Change this to your preferred region
TABLE_NAME="otp_main"

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
    --region "$AWS_REGION"

# Enable TTL on expiration_timestamp
aws dynamodb update-time-to-live \
    --table-name "$TABLE_NAME" \
    --time-to-live-specification Enabled=true,AttributeName=expiration_timestamp \
    --region "$AWS_REGION"

# Output success message
echo "DynamoDB table '$TABLE_NAME' created successfully with TTL enabled on 'expiration_timestamp'"
```

```bash
sh create_dynamodb_table.sh  aws-profile
```