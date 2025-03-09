# Generate OTP:
### * Example JSON Body for Email Request
```json
{
  "user_id": "User123",
  "method": "email",
  "recipient": "example@example.com"
}
```
#### Hardcode for Testing (Not Recommended for Production)
* If needed, try setting a default value in the Python code (generate-otp-lambda.py):

```python
SES_FROM_EMAIL = os.getenv('SES_FROM_EMAIL', 'your_verified_email@example.com')
```

## * Environment variables of the Lambda Function (`generate-otp-lambda.py`)

| Key           | value                                 |
| ------------- | --------------------------------------|
| KMS_KEY_ID    | 0cf5bb9c-8dee-41d4-99ca-63434a381758  |
| SES_FROM_EMAIL| example@example.com                   |
| --            | --                                    |

### * TEST Lambda from AWS Console (Test event):

* Test event action - Create new event
* Event name - request_otp
* Payload (Event JSON) - 

```json
{
  "body": "{\"user_id\": \"User123\", \"method\": \"email\", \"recipient\": \"example@example.com\"}"
}
```


# Verify OTP:
### * Example JSON Body for Verify OTP request.
```json
{
  "user_id": "User123",
  "otp_code": "867087"
}

```
### * Environment variables of the Lambda Function (`verify-otp-lambda.py`)

| Key           | value                                 |
| ------------- | --------------------------------------|
| KMS_KEY_ID    | 0cf5bb9c-8dee-41d4-99ca-63434a381758  |
| --            | --                                    |

### * TEST Lambda from AWS Console (Test event):

* Test event action - Create new event
* Event name - verify_otp
* Payload (Event JSON) - 
```json
{
  "body": "{\"user_id\": \"User123\", \"otp_code\": \"771941\"}"
}
```