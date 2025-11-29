// Auto-detect if running on localhost
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

window.APP_CONFIG = {
    // If local, use localhost:8000. If online, use your Render Backend URL.
    API_URL: isLocal 
        ? "http://127.0.0.1:8000" 
        : "https://student-retention-app-backend.onrender.com" // <--- PUT YOUR REAL RENDER BACKEND URL HERE
};