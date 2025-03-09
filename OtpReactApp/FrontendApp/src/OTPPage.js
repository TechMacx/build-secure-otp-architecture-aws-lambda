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
                otp_code: otp,
            });
            setMessage(response.data.message);
        } catch (error) {
            setMessage("Invalid or expired OTP");
        }
    };

    return (
        <div style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100vh",
            background: "linear-gradient(to right, #6a11cb, #2575fc)" // Background gradient
        }}>
            <div style={{
                backgroundColor: "white",
                padding: "25px",
                borderRadius: "12px",
                boxShadow: "0px 4px 15px rgba(0, 0, 0, 0.2)",
                width: "400px",
                textAlign: "center"
            }}>
                <h2 style={{ marginBottom: "20px", color: "#333" }}>OTP Authentication</h2>

                {/* Input Fields Container */}
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    <input
                        type="text"
                        placeholder="User ID"
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        style={{
                            width: "93%", // Applied only to input boxes
                            padding: "12px",
                            borderRadius: "8px",
                            border: "1px solid #ccc",
                            textAlign: "left",
                            margin: "auto"
                        }}
                    />

                    <select
                        value={method}
                        onChange={(e) => setMethod(e.target.value)}
                        style={{
                            width: "100%", // Keeping dropdown unchanged
                            padding: "12px",
                            borderRadius: "8px",
                            border: "1px solid #ccc",
                            textAlign: "left",
                            margin: "auto"
                        }}
                    >
                        <option value="email">Email</option>
                        <option value="sms">SMS</option>
                    </select>

                    <input
                        type="text"
                        placeholder={method === "email" ? "Email Address" : "Phone Number"}
                        value={recipient}
                        onChange={(e) => setRecipient(e.target.value)}
                        style={{
                            width: "93%", // Applied only to input boxes
                            padding: "12px",
                            borderRadius: "8px",
                            border: "1px solid #ccc",
                            textAlign: "left",
                            margin: "auto"
                        }}
                    />

                    <button 
                        onClick={generateOtp} 
                        style={{
                            width: "100%", // Keeping buttons unchanged
                            padding: "12px",
                            backgroundColor: "#007bff",
                            color: "white",
                            borderRadius: "8px",
                            border: "none",
                            cursor: "pointer",
                            fontWeight: "bold",
                            margin: "auto"
                        }}
                    >
                        Generate OTP
                    </button>

                    <input
                        type="text"
                        placeholder="Enter OTP"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value)}
                        style={{
                            width: "93%", // Applied only to input boxes
                            padding: "12px",
                            borderRadius: "8px",
                            border: "1px solid #ccc",
                            textAlign: "left",
                            margin: "auto"
                        }}
                    />

                    <button 
                        onClick={verifyOtp} 
                        style={{
                            width: "100%", // Keeping buttons unchanged
                            padding: "12px",
                            backgroundColor: "#28a745",
                            color: "white",
                            borderRadius: "8px",
                            border: "none",
                            cursor: "pointer",
                            fontWeight: "bold",
                            margin: "auto"
                        }}
                    >
                        Verify OTP
                    </button>
                </div>

                {message && <p style={{ marginTop: "15px", color: "#d9534f", fontWeight: "bold" }}>{message}</p>}
            </div>
        </div>
    );
}
