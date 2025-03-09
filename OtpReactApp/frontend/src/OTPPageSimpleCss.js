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
            const response = await axios.post(`${API_BASE_URL}/deliver-otp`, {
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
