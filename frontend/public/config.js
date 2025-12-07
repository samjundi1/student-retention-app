// frontend/public/config.js
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

window.APP_CONFIG = {
    API_URL: isLocal 
        ? "http://127.0.0.1:8000" 
        : "https://student-retention-app-backend.onrender.com" // <--- Ensure this is your ACTUAL Backend URL
};