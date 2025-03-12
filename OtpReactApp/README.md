# Project Structure
```pgsql
otp-app/
│── frontend/ (React App)
│   ├── src/
│   │   ├── App.js
│   │   ├── OTPPage.js
│   ├── package.json
│── README.md
```

## Step 1: Set Up the Frontend (React)

### 1. Create a React App (Optional) 
** Start from Point **`2. Install Dependencies`** If you clone `FrontendApp` from this repository.
```sh
mkdir otp-app && cd otp-app
npx create-react-app frontend
cd frontend
```
### 2. Install Dependencies 
```sh
cd frontend
npm install axios
npm install react-router-dom  # Installation required - Redirect HomePage.js after successful OTP verfication.
```
### 3. Update **`src/App.js`**
Replace **`App.js`** with:

```javascript
import OTPPage from "./OTPPage";

function App() {
    return (
        <div>
            <OTPPage />
        </div>
    );
}

export default App;
```

### 4. Create **`src/OTPPage.js`**
Inside `src/`, create `OTPPage.js` and add:

```javascript
import { useState } from "react";
import axios from "axios";
import API_BASE_URL from "./config";

export default function OTPPage() {
    const [userId, setUserId] = useState("");
    const [method, setMethod] = useState("email");
    const [recipient, setRecipient] = useState("");
    const [otp, setOtp] = useState("");
    const [message, setMessage] = useState("");

    const generateOtp = async () => {
        try {
            const response = await axios.post(`${API_BASE_URL}/generate-otp`, {
                user_id: userId,
                method,
                recipient,
            });
            setMessage(response.data.message);
        } catch (error) {
            setMessage("Error generating OTP");
        }
    };

    const verifyOtp = async () => {
        try {
            const response = await axios.post(`${API_BASE_URL}/verify-otp`, {
                user_id: userId,
                otp_code: otp,  // Fix here,
            });
            setMessage(response.data.message);
        } catch (error) {
            setMessage("Invalid or expired OTP");
        }
    };

    return (
        <div style={{ padding: "20px", maxWidth: "400px", margin: "auto", textAlign: "center" }}>
            <h2>OTP Authentication</h2>

            <input
                type="text"
                placeholder="User ID"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                style={{ display: "block", margin: "10px auto", padding: "10px", width: "100%" }}
            />

            <select
                value={method}
                onChange={(e) => setMethod(e.target.value)}
                style={{ display: "block", margin: "10px auto", padding: "10px", width: "100%" }}
            >
                <option value="email">Email</option>
                <option value="sms">SMS</option>
            </select>

            <input
                type="text"
                placeholder={method === "email" ? "Email Address" : "Phone Number"}
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                style={{ display: "block", margin: "10px auto", padding: "10px", width: "100%" }}
            />

            <button onClick={generateOtp} style={{ padding: "10px", margin: "10px", width: "100%" }}>
                Generate OTP
            </button>

            <input
                type="text"
                placeholder="Enter OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                style={{ display: "block", margin: "10px auto", padding: "10px", width: "100%" }}
            />

            <button onClick={verifyOtp} style={{ padding: "10px", margin: "10px", width: "100%" }}>
                Verify OTP
            </button>

            {message && <p style={{ marginTop: "20px", fontWeight: "bold" }}>{message}</p>}
        </div>
    );
}
```
### 5. Run the Frontend
```sh
npm start
```
## Step 2: Testing
1. Open your browser and go to http://localhost:3000.
2. Enter a User ID, select Email/SMS, and enter a Recipient (email or phone).
3. Click "Generate OTP".
4. The generated OTP will be displayed in the backend console (for testing).
5. Enter the OTP and click "Verify OTP".

## Next Steps
* Integrate AWS SES/SNS for real email/SMS delivery.
* Store OTPs in DynamoDB for persistence.
* Secure APIs with JWT Authentication.
* Deploy on AWS (ECS, Lambda, API Gateway, or EC2).
* Let me know if you need any modifications! 🚀