import React from "react";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
    const navigate = useNavigate();

    // Logout handler
    const handleLogout = () => {
        // You can clear user data or handle session cleanup here if needed
        localStorage.removeItem("userId");
        // Navigate to the OTP page
        navigate("/");  // Assuming "/otp" is the path to OTPPage.js
    };

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                height: "100vh",
                background: "linear-gradient(to right,rgb(160, 67, 0),rgb(193, 4, 105))", //"linear-gradient(to right, #FF6A00, #FF1493)", // Gradient background
                color: "white",
                fontFamily: "Arial, sans-serif",
            }}
        >
            <h1>Welcome to the Home Page!</h1>
            
            {/* Logout button */}
            <button
                onClick={handleLogout}
                style={{
                    padding: "10px 20px",
                    backgroundColor: "#FF6347",
                    color: "white",
                    border: "none",
                    borderRadius: "5px",
                    cursor: "pointer",
                    fontSize: "16px",
                    marginTop: "20px",
                    transition: "background-color 0.3s ease",
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = "#FF4500"}  //"#FF4500"
                onMouseOut={(e) => e.target.style.backgroundColor = "#FF6347"}
            >
                Logout
            </button>
        </div>
    );
}
