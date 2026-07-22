// Centralized API configuration supporting REACT_APP_BACKEND_URL, VITE_API_URL, NEXT_PUBLIC_API_URL, and API_BASE_URL
export const API_BASE_URL = (
  process.env.REACT_APP_BACKEND_URL ||
  process.env.VITE_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.API_BASE_URL ||
  "http://localhost:8000"
).replace(/\/$/, "");
