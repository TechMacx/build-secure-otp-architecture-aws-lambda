// Path: otp-app/frontend/src/OTPPage.js
// import OTPPage from "./OTPPage";
// function App() {
//     return (
//         <div>
//             <OTPPage />
//         </div>
//     );
// }

// export default App;

// Path: otp-app/frontend/src/OTPPageSimpleCss.js
// import OTPPage from "./OTPPageSimpleCss";
// function App() {
//     return (
//         <div>
//             <OTPPage />
//         </div>
//     );
// }

// export default App;

// Path: otp-app/frontend/src/OTPPageHome.js
// OTPPageHome.js otp-app/frontend/src/HomePage.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import OTPPage from './OTPPageHome';
import HomePage from './HomePage'; // Import the HomePage component

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<OTPPage />} />
                <Route path="/home" element={<HomePage />} /> {/* Route for HomePage */}
            </Routes>
        </Router>
    );
}

export default App;
