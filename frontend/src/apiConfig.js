// Centralized API configuration using REACT_APP_BACKEND_URL environment variable
export const API_BASE_URL = (
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000"
).replace(/\/$/, "");
